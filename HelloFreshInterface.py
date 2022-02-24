from datetime import date, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

class HelloFreshInterface:

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def getDayDelta(button, referenceDate):
        text = button.get_attribute("innerText")
        """
        DAY OF THE WEEK
        DAY
        MONTH
        """
        _, day, month = text.split()
        day = int(day)
        month = datetime.strptime(month, "%b").month

        return abs(date(referenceDate.year, month, day) - referenceDate)

    def getPastMeals(self):
        self.driver.get("https://www.hellofresh.com/my-account/deliveries/past-deliveries")

        # Click "Show more" until all past meals are visible. 
        while True:
            try:
                # Find and click the element. 
                clickableElement = self.driver.find_element(By.XPATH, "//*[text()='Show more']")
                clickableElement.click()
            except NoSuchElementException:
                # We successfully clicked the element. 
                break
            except StaleElementReferenceException:
                # Keep trying. 
                pass

        # Get all meals that have been previously ordered. 
        mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"
        pastMealTitles = self.driver.find_elements(By.XPATH, mealTitleXPath)
        pastMeals = [title.get_attribute('title') for title in pastMealTitles]

        return pastMeals

    def getUpcomingMeals(self, selectionDate):
        self.driver.get("https://www.hellofresh.com/my-account/deliveries/menu")
        buttons = WebDriverWait(self.driver, 6).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@data-test-id='weekly-nav-button-week']"))
        )

        # We need to click the button with the closest date after today. 
        _, button = min([(HelloFreshInterface.getDayDelta(button, selectionDate), button) for button in buttons], key=lambda l: l[0])
        buttonDataId = button.get_attribute("data-id")

        # Load the correct URL, and wait for the button that says 
        # Show/Hide nonselected meals. 
        self.driver.get(f"https://www.hellofresh.com/my-account/deliveries/menu/{buttonDataId}/17028605")
        WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'nonselected meals')]"))
        )

        try:
            clickableElement = self.driver.find_element(By.XPATH, "//*[text()='Show nonselected meals']")
            clickableElement.click()
        except NoSuchElementException:
            # This means the nonselected meals are already visible. 
            pass

        # Get all meals for the upcoming week, both selected and unselected. 
        # Exclude the premium meals. 
        mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"

        # Ensure that the meals have loaded. 
        WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, f"{mealTitleXPath}"))
        )

        recipeXPath = "div[@data-test-wrapper-id='recipe-component']"
        selectedMealsXPath = "span[@data-translation-id='my-deliveries-experiments.multiple-up.in-your-box']"
        unselectedMealsTitles = self.driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[not(@data-test-id='recipe-is-premium')][not(descendant::{selectedMealsXPath})]]")
        selectedMealsTitles = self.driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[descendant::{selectedMealsXPath}]]")
        unselectedMeals = [title.get_attribute('title') for title in unselectedMealsTitles]
        selectedMeals = [title.get_attribute('title') for title in selectedMealsTitles]

        return (selectedMeals, unselectedMeals)

    def selectMeals(self, selectionDate, selectedMeals):
        self.driver.get("https://www.hellofresh.com/my-account/deliveries/menu")
        buttons = WebDriverWait(self.driver, 6).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@data-test-id='weekly-nav-button-week']"))
        )

        # We need to click the button with the closest date after today. 
        _, button = min([(HelloFreshInterface.getDayDelta(button, selectionDate), button) for button in buttons], key=lambda l: l[0])
        buttonDataId = button.get_attribute("data-id")

        # Load the correct URL, and wait for the button that says 
        # Show/Hide nonselected meals. 
        self.driver.get(f"https://www.hellofresh.com/my-account/deliveries/menu/{buttonDataId}/17028605")
        WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'nonselected meals')]"))
        )

        try:
            clickableElement = self.driver.find_element(By.XPATH, "//*[text()='Show nonselected meals']")
            clickableElement.click()
        except NoSuchElementException:
            # This means the nonselected meals are already visible. 
            pass

        # Ensure that the meals have loaded. 
        mealTitleXPath = "//h4[@data-test-id='recipe-card-title']" 
        WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, f"{mealTitleXPath}"))
        )

        # Find all currently selected meals. Remove the incorrectly 
        # selected meals. 
        recipeXPath = "div[@data-test-wrapper-id='recipe-component']"
        selectedMealsXPath = "span[@data-translation-id='my-deliveries-experiments.multiple-up.in-your-box']"
        decreaseButtonXPath = "//button[@data-test-id='multiple-up-decrease-button']"

        # Find all currently selected meals and note the ones that are 
        # not included in the list of predicted selected meals. 
        mealsToRemove = []
        alreadySelectedMeals = []
        currentlySelectedMeals = self.driver.find_elements(By.XPATH, f"//{recipeXPath}[descendant::{selectedMealsXPath}]")
        for meal in currentlySelectedMeals:
            mealTitleElement = meal.find_element(By.XPATH, f".{mealTitleXPath}")
            mealTitle = mealTitleElement.get_attribute("title")
            if mealTitle not in selectedMeals:
                mealsToRemove.append(mealTitle)
            else:
                alreadySelectedMeals.append(mealTitle)

        for meal in mealsToRemove:
            meal = self.driver.find_element(By.XPATH, f"//{recipeXPath}[descendant::{selectedMealsXPath}][descendant::*[text()='{meal}']]")

            decreaseButton = meal.find_element(By.XPATH, f".{decreaseButtonXPath}")
            decreaseButton.click()

        mealsToSelect = list(set(selectedMeals) - set(alreadySelectedMeals))

        # For the remaining meals that we need to select, click the 
        # "Add extra meal" button. 
        for meal in selectedMeals:
            pass