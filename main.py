import sys
import pathlib
from pickle import dump
from datetime import date, datetime
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface
from analyzeData import Analyze

def getPastMeals():
    try:
        driver = ChromeDriver(f"{pathlib.Path(__file__).parent.resolve()}/config.ini")

        helloFreshInterface = HelloFreshInterface(driver.driver)
        pastMeals = helloFreshInterface.getPastMeals()
        today = date.today()
        selectedMeals, unselectedMeals = helloFreshInterface.getUpcomingMeals(today)
        selectedMeals += pastMeals

        with open("selected-meals.pickle", "wb") as f:
            dump(selectedMeals, f)
        with open("unselected-meals.pickle", "wb") as f:
            dump(unselectedMeals, f)
    finally:
        driver.closeChrome()

def getUpcomingMeals(selectionDate):
    try:
        driver = ChromeDriver(f"{pathlib.Path(__file__).parent.resolve()}/config.ini")

        helloFreshInterface = HelloFreshInterface(driver.driver)
        selectedMeals, unselectedMeals = helloFreshInterface.getUpcomingMeals(selectionDate)
        meals = selectedMeals + unselectedMeals

        with open("upcoming-meals.pickle", "wb") as f:
            dump(meals, f)
    finally:
        driver.closeChrome()

def predictMealSelections():
    analyzer = Analyze()
    analyzer.selectMeals()
    print(analyzer.scores)

def saveMealSelections(selectionDate):
    analyzer = Analyze()
    analyzer.selectMeals()
    scores = analyzer.scores

    # These are the 5 meals we'll select. 
    top5Meals = [meal[0] for meal in scores[:5]]
    print(top5Meals)

    try:
        driver = ChromeDriver(f"{pathlib.Path(__file__).parent.resolve()}/config.ini")

        helloFreshInterface = HelloFreshInterface(driver.driver)
        helloFreshInterface.selectMeals(selectionDate, top5Meals)
    finally:
        driver.closeChrome()

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

if action == "h":
    getPastMeals()
elif action == "u":
    getUpcomingMeals(selectionDate)
elif action == "p":
    predictMealSelections()
elif action == "s":
    saveMealSelections(selectionDate)
elif action == "a":
    getPastMeals()
    getUpcomingMeals(selectionDate)
    saveMealSelections(selectionDate)
else:
    usage()