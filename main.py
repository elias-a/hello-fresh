import os
import argparse
import logging
import pickle
from configparser import ConfigParser
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface
from Analyze import Analyze

class HelloFreshController:
    def __init__(self, driver, subscriptionId, email, password):
        self._helloFreshInterface = HelloFreshInterface(driver, subscriptionId)
        self._helloFreshInterface.authenticate(email, password)

    def getPastMeals(self):
        logging.info("Getting past meals...")
        pastMeals = self._helloFreshInterface.getPastMeals()

        logging.info(f"{len(pastMeals)} past meals found. Writing to file...")
        with open(os.path.join(os.path.dirname(__file__), "past-meals.pickle"), "wb") as f:
            pickle.dump(pastMeals, f)

    def getUpcomingMeals(self):
        logging.info("Getting upcoming meals...")
        selectedMeals, unselectedMeals = self._helloFreshInterface.getUpcomingMeals()
        meals = selectedMeals + unselectedMeals

        logging.info(f"{len(meals)} upcoming meals found. Writing to file...")
        with open(os.path.join(os.path.dirname(__file__), "upcoming-meals.pickle"), "wb") as f:
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

        selectedMeals, _ = self._helloFreshInterface.getUpcomingMeals()
        self._helloFreshInterface.selectMeals(selectedMeals, top5Meals)

logging.basicConfig(
    filename="hello-fresh.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Starting HelloFresh meal selection program...")

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
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
subscriptionId = config["HELLO_FRESH"]["subscriptionId"]
email = config["HELLO_FRESH"]["email"]
password = config["HELLO_FRESH"]["password"]

logging.info("Opening Chrome...")
driver = ChromeDriver()
driver.initDriver()

helloFreshController = HelloFreshController(driver.driver, subscriptionId, email, password)
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
    logging.error(e)

