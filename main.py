import sys
from pickle import dump
from datetime import date
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface
from analyzeData import Analyze

def getPastMeals():
    try:
        driver = ChromeDriver("config.ini")

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
        driver = ChromeDriver("config.ini")

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
        driver = ChromeDriver("config.ini")

        helloFreshInterface = HelloFreshInterface(driver.driver)
        helloFreshInterface.selectMeals(selectionDate, top5Meals)
    finally:
        driver.closeChrome()

selectionDate = date(2022, 4, 17)

def usage():
    print("Usage: python main.py {h|u|p|s|a}\n"
        + f"{' ' * 4}h: Get meal history\n"
        + f"{' ' * 4}u: Get meals for an upcoming week\n"
        + f"{' ' * 4}p: Predict meal selections for an upcoming week\n"
        + f"{' ' * 4}s: Save meal selections online\n"
        + f"{' ' * 4}a: Get meal history, get upcoming meals, and save "
        + "predicted meal selections"
    )

try:
    arg = sys.argv[1]
except IndexError:
    usage()
    sys.exit(1)

if arg == "h":
    getPastMeals()

elif arg == "u":
    getUpcomingMeals(selectionDate)

elif arg == "p":
    predictMealSelections()

elif arg == "s":
    saveMealSelections(selectionDate)

elif arg == "a":
    getPastMeals()
    getUpcomingMeals()
    saveMealSelections()

else:
    usage()