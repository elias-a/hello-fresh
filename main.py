import sys
from pickle import dump
from datetime import date
from helpers import initDriver
from getData import getPastMeals, getUpcomingMeals

def switch(arg):
    args = ["h", "u"]
    if arg not in args:
        return

    driver = initDriver()

    if arg == "h":
        # 
        pastMeals = getPastMeals(driver)
        today = date.today()
        selectedMeals, unselectedMeals = getUpcomingMeals(driver, today)
        selectedMeals += pastMeals

        with open("selected-meals.pickle", "wb") as f:
            dump(selectedMeals, f)
        with open("unselected-meals.pickle", "wb") as f:
            dump(unselectedMeals, f)

    elif arg == "u":
        selectionDate = date(2021, 2, 27)
        selectedMeals, unselectedMeals = getUpcomingMeals(driver, selectionDate)
        meals = selectedMeals + unselectedMeals

        with open("upcoming-meals.pickle", "wb") as f:
            dump(unselectedMeals, f)

    driver.quit()

def usage():
    print(f"Usage: python main.py [h | u]")

try:
    switch(sys.argv[1])
except IndexError:
    usage()