import re
import time
import logging
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class HelloFreshInterface:
    _url = "https://www.hellofresh.com/my-account/deliveries"

    def __init__(self, driver, subscriptionId, deliveryDayOfWeek = 5, timeout = 3):
        self.driver = driver
        self.subscriptionId = subscriptionId
        self._timeout = 2
        self._selectionDate = HelloFreshInterface.getNextDeliveryDate(deliveryDayOfWeek)

    @staticmethod
    def getNextDeliveryDate(deliveryDayOfWeek):
        if not (isinstance(deliveryDayOfWeek, int) and deliveryDayOfWeek >= 0 and deliveryDayOfWeek <= 6):
            raise Exception("\"deliveryDayOfWeek\" must be an integer in [0, 6].")

        today = date.today()
        delta = timedelta((7 + deliveryDayOfWeek - today.weekday()) % 7)
        return (today + delta).strftime('%Y-%m-%d')

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

    def getPastMeals(self):
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
        pastMeals = [title.get_attribute('title') for title in pastMealTitles]

        return pastMeals

    def _navigateToDate(self):
        buttonXPath = "//span[@data-element='Button' and .//span[text()='18'] and .//span[text()='Feb']]"
        buttonIsLoaded = EC.element_to_be_clickable((By.XPATH, buttonXPath))
        button = WebDriverWait(self.driver, self._timeout).until(buttonIsLoaded)
        self.driver.execute_script("arguments[0].click();", button)

    def getUpcomingMeals(self):
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

        return (selectedTitles, unselectedTitles)

    def selectMeals(self, selectedMeals, mealsToSelect):
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

        # Don't add any extras.
        logging.info("Not adding any extras...")
        skipXPath = "//button[@data-test-id='skip-extras-button']"
        skipIsLoaded = EC.element_to_be_clickable((By.XPATH, skipXPath))
        skip = WebDriverWait(self.driver, self._timeout).until(skipIsLoaded)
        self.driver.execute_script("arguments[0].click();", skip)

        # Wait for processing complete.
        completeXPath = "//span[text()='Order complete!']"
        completeIsLoaded = EC.presence_of_element_located((By.XPATH, completeXPath))
        complete = WebDriverWait(self.driver, self._timeout).until(completeIsLoaded)
        logging.info("Meal selection complete!")

