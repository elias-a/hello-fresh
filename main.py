import sys
import pathlib
from pickle import dump
from datetime import date, datetime
from configparser import ConfigParser
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface
from analyzeData import Analyze

def getPastMeals(driver, subscriptionId):
    helloFreshInterface = HelloFreshInterface(driver.driver, subscriptionId)
    pastMeals = helloFreshInterface.getPastMeals()
    today = date.today()
    selectedMeals, unselectedMeals = helloFreshInterface.getUpcomingMeals(today)
    selectedMeals += pastMeals

    with open(f"{pathlib.Path(__file__).parent.resolve()}/selected-meals.pickle", "wb") as f:
        dump(selectedMeals, f)
    with open(f"{pathlib.Path(__file__).parent.resolve()}/unselected-meals.pickle", "wb") as f:
        dump(unselectedMeals, f)

def getUpcomingMeals(driver, selectionDate, subscriptionId):
    helloFreshInterface = HelloFreshInterface(driver.driver, subscriptionId)
    selectedMeals, unselectedMeals = helloFreshInterface.getUpcomingMeals(selectionDate)
    meals = selectedMeals + unselectedMeals

    with open(f"{pathlib.Path(__file__).parent.resolve()}/upcoming-meals.pickle", "wb") as f:
        dump(meals, f)

def predictMealSelections():
    analyzer = Analyze()
    analyzer.selectMeals()
    print(analyzer.scores)

def saveMealSelections(driver, selectionDate, subscriptionId):
    analyzer = Analyze()
    analyzer.selectMeals()
    scores = analyzer.scores

    # These are the 5 meals we'll select. 
    top5Meals = [meal[0] for meal in scores[:5]]
    print(top5Meals)

    helloFreshInterface = HelloFreshInterface(driver.driver, subscriptionId)
    helloFreshInterface.selectMeals(selectionDate, top5Meals)

def usage():
    print("Usage: python main.py {h|u|p|s|a} DATE\n"
        + f"{' ' * 4}h: Get meal history\n"
        + f"{' ' * 4}u: Get meals for an upcoming week\n"
        + f"{' ' * 4}p: Predict meal selections for an upcoming week\n"
        + f"{' ' * 4}s: Save meal selections online\n"
        + f"{' ' * 4}a: Get meal history, get upcoming meals, and save "
        + "predicted meal selections"
    )

if len(sys.argv) == 3:
    action = sys.argv[1]
    selectionDate = datetime.strptime(sys.argv[2], '%m/%d/%Y').date()
else:
    usage()
    sys.exit(1)

config = ConfigParser()
configPath = f"{pathlib.Path(__file__).parent.resolve()}/config.ini"
config.read(configPath)
subscriptionId = config["HELLO_FRESH"]["subscriptionId"]

if action == "h":
    try:
        driver = ChromeDriver(configPath)
        getPastMeals(driver, subscriptionId)
    finally:
        driver.closeChrome()
elif action == "u":
    try:
        driver = ChromeDriver(configPath)
        getUpcomingMeals(driver, selectionDate, subscriptionId)
    finally:
        driver.closeChrome()
elif action == "p":
    predictMealSelections()
elif action == "s":
    try:
        driver = ChromeDriver(configPath)
        saveMealSelections(driver, selectionDate, subscriptionId)
    finally:
        driver.closeChrome()
elif action == "a":
    try:
        driver = ChromeDriver(configPath)
        getPastMeals(driver, subscriptionId)
        getUpcomingMeals(driver, selectionDate, subscriptionId)
        saveMealSelections(driver, selectionDate, subscriptionId)
    finally:
        driver.closeChrome()
else:
    usage()