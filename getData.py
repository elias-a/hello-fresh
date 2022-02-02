import csv
import pathlib
from pickle import dump
from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

directory = pathlib.Path(__file__).parent.resolve()

with open(f"{directory}/config.csv", "r") as f:
    reader = csv.reader(f)
    email, password, chromedriver, port = list(reader)[0]

options = Options()
options.headless = True
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
driver = webdriver.Chrome(chromedriver, options=options)

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

driver.get("https://www.hellofresh.com/my-account/deliveries/menu")
buttons = WebDriverWait(driver, 6).until(
    EC.presence_of_all_elements_located((By.XPATH, "//button[@data-test-id='weekly-nav-button-week']"))
)

# We need to click the button with the closest date after today. 
today = date.today()
currentDay = today.day
currentMonth = today.month

def getDayDelta(button):
    text = button.get_attribute("innerText")
    """
    DAY OF THE WEEK
    DAY
    MONTH
    """
    _, day, month = text.split()
    day = int(day)
    month = datetime.strptime(month, "%b").month

    return date(today.year, month, day) - today

_, button = min([(getDayDelta(button), button) for button in buttons], key=lambda l: l[0])
button.click()

# TODO: Need some indication that the correct date is selected. 
WebDriverWait(driver, 6).until(
    EC.presence_of_all_elements_located((By.XPATH, mealTitleXPath))
)

# Get all meals for the upcoming week, both selected and unselected. 
# Exclude the premium meals. 
recipeXPath = "div[@data-test-wrapper-id='recipe-component']"
selectedMealsXPath = "span[@data-translation-id='my-deliveries-experiments.multiple-up.in-your-box']"
unselectedMealsTitles = driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[not(@data-test-id='recipe-is-premium')][not(descendant::{selectedMealsXPath})]]")
selectedMealsTitles = driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[descendant::{selectedMealsXPath}]]")
unselectedMeals = [title.get_attribute('title') for title in unselectedMealsTitles]
selectedMeals = [title.get_attribute('title') for title in selectedMealsTitles]

selectedMeals += pastMeals

with open("selected-meals.pickle", "wb") as f:
    dump(selectedMeals, f)
with open("unselected-meals.pickle", "wb") as f:
    dump(unselectedMeals, f)

driver.quit()