from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from helpers import getDayDelta

def getPastMeals(driver):
    driver.get("https://www.hellofresh.com/my-account/deliveries/past-deliveries")

    # Click "Show more" until all past meals are visible. 
    while True:
        try:
            # Find and click the element. 
            clickableElement = driver.find_element(By.XPATH, "//*[text()='Show more']")
            clickableElement.click()
        except NoSuchElementException:
            # We successfully clicked the element. 
            break
        except StaleElementReferenceException:
            # Keep trying. 
            pass

    # Get all meals that have been previously ordered. 
    mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"
    pastMealTitles = driver.find_elements(By.XPATH, mealTitleXPath)
    pastMeals = [title.get_attribute('title') for title in pastMealTitles]

    return pastMeals

def getUpcomingMeals(driver, selectionDate):
    driver.get("https://www.hellofresh.com/my-account/deliveries/menu")
    buttons = WebDriverWait(driver, 6).until(
        EC.presence_of_all_elements_located((By.XPATH, "//button[@data-test-id='weekly-nav-button-week']"))
    )

    # We need to click the button with the closest date after today. 
    _, button = min([(getDayDelta(button, selectionDate), button) for button in buttons], key=lambda l: l[0])
    buttonDataId = button.get_attribute("data-id")

    # Load the correct URL, and wait for the button that says 
    # Show/Hide nonselected meals. 
    driver.get(f"https://www.hellofresh.com/my-account/deliveries/menu/{buttonDataId}/17028605")
    WebDriverWait(driver, 6).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'nonselected meals')]"))
    )

    try:
        clickableElement = driver.find_element(By.XPATH, "//*[text()='Show nonselected meals']")
        clickableElement.click()
    except NoSuchElementException:
        # This means the nonselected meals are already visible. 
        pass

    # Get all meals for the upcoming week, both selected and unselected. 
    # Exclude the premium meals. 
    mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"

    # Ensure that the meals have loaded. 
    WebDriverWait(driver, 6).until(
        EC.presence_of_element_located((By.XPATH, f"{mealTitleXPath}"))
    )

    recipeXPath = "div[@data-test-wrapper-id='recipe-component']"
    selectedMealsXPath = "span[@data-translation-id='my-deliveries-experiments.multiple-up.in-your-box']"
    unselectedMealsTitles = driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[not(@data-test-id='recipe-is-premium')][not(descendant::{selectedMealsXPath})]]")
    selectedMealsTitles = driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[descendant::{selectedMealsXPath}]]")
    unselectedMeals = [title.get_attribute('title') for title in unselectedMealsTitles]
    selectedMeals = [title.get_attribute('title') for title in selectedMealsTitles]

    return (selectedMeals, unselectedMeals)