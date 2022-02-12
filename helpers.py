import csv
import pathlib
from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def initDriver():
    directory = pathlib.Path(__file__).parent.resolve()

    with open(f"{directory}/config.csv", "r") as f:
        reader = csv.reader(f)
        email, password, chromedriver, port = list(reader)[0]

    options = Options()
    options.headless = True
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    driver = webdriver.Chrome(chromedriver, options=options)

    return driver

def getDayDelta(button, referenceDate):
    text = button.get_attribute("innerText")
    """
    DAY OF THE WEEK
    DAY
    MONTH
    """
    _, day, month = text.split()
    day = int(day)
    month = datetime.strptime(month, "%b").month

    return abs(date(referenceDate.year, month, day) - referenceDate)