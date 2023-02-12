import argparse
import pathlib
import pickle
from configparser import ConfigParser
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface
from Analyze import Analyze

class HelloFreshController:
    def __init__(self, driver, subscriptionId):
        self._helloFreshInterface = HelloFreshInterface(driver.driver, subscriptionId)

    def getPastMeals(self):
        pastMeals = self._helloFreshInterface.getPastMeals()

        with open(f"{pathlib.Path(__file__).parent.resolve()}/past-meals.pickle", "wb") as f:
            pickle.dump(pastMeals, f)

    def getUpcomingMeals(self):
        selectedMeals, unselectedMeals = self._helloFreshInterface.getUpcomingMeals(selectionDate)
        meals = selectedMeals + unselectedMeals

        with open(f"{pathlib.Path(__file__).parent.resolve()}/upcoming-meals.pickle", "wb") as f:
            pickle.dump(meals, f)

    def predictMealSelections(self):
        analyzer = Analyze()
        analyzer.selectMeals()
        print(analyzer.scores)

    def saveMealSelections(self):
        analyzer = Analyze()
        analyzer.selectMeals()
        scores = analyzer.scores

        # These are the 5 meals we'll select. 
        top5Meals = [meal[0] for meal in scores[:5]]
        print(top5Meals)

        self._helloFreshInterface.selectMeals(selectionDate, top5Meals)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--action",
    required=True,
    choices=["history", "upcoming", "predict", "save", "all"],
    help="Choose the action to perform",
)
args = parser.parse_args()
action = args.action

config = ConfigParser()
configPath = f"{pathlib.Path(__file__).parent.resolve()}/config.ini"
config.read(configPath)
subscriptionId = config["HELLO_FRESH"]["subscriptionId"]

driver = ChromeDriver(configPath)
helloFreshController = HelloFreshController(driver, subscriptionId)
try:
    match action:
        case "history":
            helloFreshController.getPastMeals()
        case "upcoming":
            helloFreshController.getUpcomingMeals()
        case "predict":
            helloFreshController.predictMealSelections()
        case "save":
            helloFreshController.saveMealSelections()
        case "all":
            helloFreshController.getPastMeals()
            helloFreshController.getUpcomingMeals()
            helloFreshController.saveMealSelections()
        case _:
            raise Exception(
                "\"action\" should be one of {\"history\", \"upcoming\", \"predict\", \"save\", \"all\"}."
            )
except Exception as e:
    print(e)
finally:
    driver.closeChrome()

