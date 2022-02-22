import sys
from pickle import dump
from datetime import date
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface
from analyzeData import Analyze

def usage():
    print("Usage: python main.py {h|u|p|s}\n"
        + f"{' ' * 4}h: Get meal history\n"
        + f"{' ' * 4}u: Get meals for an upcoming week\n"
        + f"{' ' * 4}p: Predict meal selections for an upcoming week\n"
        + f"{' ' * 4}s: Save meal selections online"
    )

try:
    arg = sys.argv[1]
except IndexError:
    usage()
    sys.exit(1)

if arg == "h":
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

elif arg == "u":
    try:
        driver = ChromeDriver("config.ini")

        helloFreshInterface = HelloFreshInterface(driver.driver)
        selectionDate = date(2021, 2, 27)
        selectedMeals, unselectedMeals = helloFreshInterface.getUpcomingMeals(selectionDate)
        meals = selectedMeals + unselectedMeals

        with open("upcoming-meals.pickle", "wb") as f:
            dump(meals, f)
    finally:
        driver.closeChrome()

elif arg == "p":
    analyzer = Analyze()
    analyzer.selectMeals()
    print(analyzer.scores)

elif arg == "s":
    analyzer = Analyze()
    analyzer.selectMeals()
    scores = analyzer.scores

    try:
        driver = ChromeDriver("config.ini")


    finally:
        driver.closeChrome()
    
else:
    usage()