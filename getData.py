import csv
import pathlib
from pickle import dump
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

directory = pathlib.Path(__file__).parent.resolve()

with open(f"{directory}/config.csv", "r") as f:
    reader = csv.reader(f)
    email, password, chromedriver, port = list(reader)[0]

options = Options()
options.headless = True
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
driver = webdriver.Chrome(chromedriver, options=options)

# Get all meals that have been previously ordered. 
mealTitleXPath = "//h4[@data-test-id='recipe-card-title']"
pastMealTitles = driver.find_elements(By.XPATH, mealTitleXPath)
pastMeals = [title.get_attribute('title') for title in pastMealTitles]

# TODO: Add logic to navigate to second page. 
driver.get("")

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