from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from helpers import initDriver, getDayDelta

driver = initDriver()

driver.get("https://www.hellofresh.com/my-account/deliveries/menu")
buttons = WebDriverWait(driver, 6).until(
    EC.presence_of_all_elements_located((By.XPATH, "//button[@data-test-id='weekly-nav-button-week']"))
)

# We need to click the button with the closest date to our desired date. 
selectionDate = date(2021, 2, 20)
_, button = min([(getDayDelta(button, selectionDate), button) for button in buttons], key=lambda l: abs(l[0]))
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

# Get all meals for the upcoming week. 
# Exclude the premium meals. 
mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"
recipeXPath = "div[@data-test-wrapper-id='recipe-component']"
upcomingMealTitles = driver.find_elements(By.XPATH, f"{mealTitleXPath}[ancestor::{recipeXPath}[not(@data-test-id='recipe-is-premium')]]")
upcomingMeals = [title.get_attribute('title') for title in upcomingMealTitles]

driver.quit()