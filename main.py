import os
import logging
from configparser import ConfigParser
from ChromeDriver import ChromeDriver
from HelloFreshInterface import HelloFreshInterface

logging.basicConfig(
    filename="hello-fresh.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Starting HelloFresh meal selection program...")

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
subscriptionId = config["HELLO_FRESH"]["subscriptionId"]
email = config["HELLO_FRESH"]["email"]
password = config["HELLO_FRESH"]["password"]

logging.info("Opening Chrome...")
driver = ChromeDriver()
driver.initDriver()

try:
    helloFreshInterface = HelloFreshInterface(driver.driver, subscriptionId)
    helloFreshInterface.authenticate(email, password)
    helloFreshInterface.predictAndSelect()
except Exception as e:
    logging.error(e)
finally:
    logging.info("Exiting program...")

