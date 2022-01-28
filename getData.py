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

mealTitles = driver.find_elements(By.XPATH, "//h4[@data-test-id='recipe-card-title']")
meals = [title.get_attribute('title') for title in mealTitles]

with open("meals.pickle", "wb") as f:
    dump(meals, f)

driver.quit()