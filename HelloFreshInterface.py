import re
import time
import logging
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from Analyze import Analyze

class HelloFreshInterface:
    _url = "https://www.hellofresh.com/my-account/deliveries"

    def __init__(self, driver, subscriptionId, deliveryDayOfWeek = 5, timeout = 3):
        self.driver = driver
        self.subscriptionId = subscriptionId
        self._timeout = timeout

        nextDeliveryDate = HelloFreshInterface._getNextDeliveryDate(deliveryDayOfWeek)
        self._month = nextDeliveryDate["month"]
        self._day = nextDeliveryDate["day"]

    @staticmethod
    def _getNextDeliveryDate(deliveryDayOfWeek):
        if not (isinstance(deliveryDayOfWeek, int) and deliveryDayOfWeek >= 0 and deliveryDayOfWeek <= 6):
            raise Exception("\"deliveryDayOfWeek\" must be an integer in [0, 6].")

        today = date.today()
        todayDayOfWeek = today.weekday()

        # Assume the last day to select meals is 5 days
        # before the delivery date.
        selectionDayOfWeek = (deliveryDayOfWeek - 5) % 7
        mod = 14 if todayDayOfWeek > selectionDayOfWeek else 7

        delta = timedelta((7 + deliveryDayOfWeek - todayDayOfWeek) % mod)
        nextDeliveryDate = today + delta

        return {
            "month": nextDeliveryDate.strftime("%b"),
            "day": nextDeliveryDate.strftime("%d"),
        }

    def _scrollToBottom(self):
        logging.info("Trying to scroll to the bottom of the screen...")
        height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            newHeight = self.driver.execute_script("return document.body.scrollHeight")

            if newHeight == height:
                break
            height = newHeight

    def authenticate(self, email, password):
        logging.info("Attempting to log in...")
        self.driver.get("https://hellofresh.com/login")

        logging.info("Entering email...")
        emailXPath = "//input[@id='hf-form-group-username-input']"
        emailIsLoaded = EC.presence_of_element_located((By.XPATH, emailXPath))
        emailElement = WebDriverWait(self.driver, self._timeout).until(emailIsLoaded)
        emailElement.send_keys(email)

        logging.info("Entering password...")
        passwordXPath = "//input[@id='hf-form-group-password-input']"
        passwordIsLoaded = EC.presence_of_element_located((By.XPATH, passwordXPath))
        passwordElement = WebDriverWait(self.driver, self._timeout).until(passwordIsLoaded)
        passwordElement.send_keys(password)

        logging.info("Logging in...")
        buttonXPath = "//button[@data-test-id='hf-login-email-password-form-submit-button']"
        buttonIsClickable = EC.element_to_be_clickable((By.XPATH, buttonXPath))
        button = WebDriverWait(self.driver, self._timeout).until(buttonIsClickable)
        self.driver.execute_script("arguments[0].click();", button)

        # Wait for login process to complete.
        pageIsLoadedXPath = "//a[@title='My Menu']"
        pageIsLoaded = EC.presence_of_element_located((By.XPATH, pageIsLoadedXPath))
        WebDriverWait(self.driver, self._timeout).until(pageIsLoaded)

    def predictAndSelect(self):
        pastMeals = self.getPastMeals()
        selectedMeals, unselectedMeals = self.getUpcomingMeals()
        upcomingMeals = selectedMeals + unselectedMeals

        analyzer = Analyze()
        scores = analyzer.selectMeals(pastMeals, upcomingMeals)

        # These are the 5 meals we'll select.
        top5Meals = [meal[0] for meal in scores[:5]]
        logging.info(f"Top 5 meals by score: {top5Meals}")

        self.selectMeals(selectedMeals, top5Meals)

    def getPastMeals(self):
        logging.info("Getting past meals...")
        url = f"{self._url}/past-deliveries?subscriptionId={self.subscriptionId}"
        logging.info(f"Navigating to {url}...")
        self.driver.get(url)

        # Click "Show more" until all past meals are visible. 
        while True:
            try:
                # Find and click the element.
                logging.info("Trying to click \"Show more\" to display past meals...")
                elementXPath = "//*[text()='Show more']"
                elementIsLoaded = EC.element_to_be_clickable((By.XPATH, elementXPath))
                element = WebDriverWait(self.driver, self._timeout).until(elementIsLoaded)
                self.driver.execute_script("arguments[0].click();", element)
            except StaleElementReferenceException:
                # Keep trying.
                continue
            except TimeoutException:
                break

        # Get all meals that have been previously ordered. 
        mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"
        pastMealTitles = self.driver.find_elements(By.XPATH, mealTitleXPath)
        pastMeals = [title.get_attribute("title") for title in pastMealTitles]

        logging.info(f"{len(pastMeals)} past meals found...")
        return pastMeals

    def _navigateToDate(self):
        buttonXPath = (
            "//span[@data-element='Button' and "
            f".//span[text()='{self._day}'] and "
            f".//span[text()='{self._month}']]"
        )
        buttonIsLoaded = EC.element_to_be_clickable((By.XPATH, buttonXPath))
        button = WebDriverWait(self.driver, self._timeout).until(buttonIsLoaded)
        self.driver.execute_script("arguments[0].click();", button)

    def getUpcomingMeals(self):
        logging.info("Getting upcoming meals...")
        url = f"{self._url}/menu"
        logging.info(f"Navigating to {url}...")
        self.driver.get(url)
        self._navigateToDate()
        self._scrollToBottom()

        titleXPath = "//h4[@data-test-id='recipe-card-title']"
        recipeXPath = "ancestor::div[@data-test-wrapper-id='recipe-component']"
        boxXPath = "descendant::*[contains(text(), 'in your box')]"
        premiumXPath = "not(descendant::div[@data-test-id='label-premium-picks'])"

        # Find all meals, excluding the premium meals.
        selectedXPath = f"{titleXPath}[{recipeXPath}[{premiumXPath} and {boxXPath}]]"
        unselectedXPath = f"{titleXPath}[{recipeXPath}[{premiumXPath} and not({boxXPath})]]"
        selectedMeals = self.driver.find_elements(By.XPATH, selectedXPath)
        unselectedMeals = self.driver.find_elements(By.XPATH, unselectedXPath)
        selectedTitles = [meal.text for meal in selectedMeals]
        unselectedTitles = [meal.text for meal in unselectedMeals]

        logging.info(f"{len(selectedTitles + unselectedTitles)} upcoming meals found...")
        return (selectedTitles, unselectedTitles)

    def selectMeals(self, selectedMeals, mealsToSelect):
        logging.info("Selecting meals...")
        url = f"{self._url}/menu"
        logging.info(f"Navigating to {url}...")
        self.driver.get(url)
        self._navigateToDate()
        self._scrollToBottom()

        mealsToAdd = set(mealsToSelect) - set(selectedMeals)
        logging.info(f"Adding meals: {mealsToAdd}...")
        mealsToRemove = set(selectedMeals) - set(mealsToSelect)
        logging.info(f"Removing meals: {mealsToRemove}...")

        # If no meals need to be added or removed, exit the method.
        if len(mealsToAdd) == 0 and len(mealsToRemove) == 0:
            logging.info("No meals to select. Meal selection complete!")
            return

        # Remove the selected meals that are not in the list of desired meals.
        for meal in mealsToRemove:
            logging.info(f"Removing meal: {meal}...")
            removeXPath = f"//button[@title='Remove 1 {meal}']"
            removeIsLoaded = EC.element_to_be_clickable((By.XPATH, removeXPath))
            remove = WebDriverWait(self.driver, self._timeout).until(removeIsLoaded)
            self.driver.execute_script("arguments[0].click();", remove)

        # Add the meals that are in the list of desired meals but not yet selected.
        mealStartXPath = "ancestor::div[@data-test-wrapper-id='recipe-component' and "
        for meal in mealsToAdd:
            logging.info(f"Adding meal: {meal}...")
            mealTitleXPath = f"descendant::h4[@title='{meal}']]"
            addXPath = f"//span[text()='Add'][{mealStartXPath + mealTitleXPath}]"
            addIsLoaded = EC.element_to_be_clickable((By.XPATH, addXPath))
            add = WebDriverWait(self.driver, self._timeout).until(addIsLoaded)
            self.driver.execute_script("arguments[0].click();", add)

        # Save the selections.
        logging.info("Saving the selections...")
        saveXPath = "//button[@data-test-id='SaveButton']"
        saveIsLoaded = EC.element_to_be_clickable((By.XPATH, saveXPath))
        save = WebDriverWait(self.driver, self._timeout).until(saveIsLoaded)
        self.driver.execute_script("arguments[0].click();", save)

        # Confirm order.
        logging.info("Confirming order...")
        confirmXPath = "//div[text()='Confirm order']"
        confirmIsLoaded = EC.element_to_be_clickable((By.XPATH, confirmXPath))
        confirm = WebDriverWait(self.driver, self._timeout).until(confirmIsLoaded)
        self.driver.execute_script("arguments[0].click();", confirm)

        # Wait for processing complete.
        completeXPath = "//div[contains(text(), 'Yum!')]"
        completeIsLoaded = EC.presence_of_element_located((By.XPATH, completeXPath))
        complete = WebDriverWait(self.driver, self._timeout).until(completeIsLoaded)
        logging.info("Meal selection complete!")

