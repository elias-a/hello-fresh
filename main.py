import sys
from pickle import dump
from datetime import date
from helpers import initDriver
from getData import getPastMeals, getUpcomingMeals
from analyzeData import Analyze

def switch(arg):
    args = ["h", "u", "s"]
    if arg not in args:
        return

    if arg == "h":
        driver = initDriver()

        # 
        pastMeals = getPastMeals(driver)
        today = date.today()
        selectedMeals, unselectedMeals = getUpcomingMeals(driver, today)
        selectedMeals += pastMeals

        with open("selected-meals.pickle", "wb") as f:
            dump(selectedMeals, f)
        with open("unselected-meals.pickle", "wb") as f:
            dump(unselectedMeals, f)

        driver.quit()

    elif arg == "u":
        driver = initDriver()

        selectionDate = date(2021, 2, 27)
        selectedMeals, unselectedMeals = getUpcomingMeals(driver, selectionDate)
        meals = selectedMeals + unselectedMeals

        with open("upcoming-meals.pickle", "wb") as f:
            dump(meals, f)

        driver.quit()

    elif arg == "s":
        analyzer = Analyze()
        analyzer.selectMeals()
        print(analyzer.scores)

def usage():
    print("Usage: python main.py {h|u|s}\n"
        + f"{' ' * 4}h: Get meal history\n"
        + f"{' ' * 4}u: Get meals for an upcoming week\n"
        + f"{' ' * 4}s: Select meals for an upcoming week"
    )

try:
    switch(sys.argv[1])
except IndexError:
    usage()