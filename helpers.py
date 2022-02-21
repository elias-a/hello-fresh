import csv
import pathlib
import subprocess
from configparser import ConfigParser
from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def isPortInUse(port):
    completedProcess = subprocess.run(["lsof", f"-i:{port}"], stdout=subprocess.DEVNULL)
    return completedProcess.returncode == 0

def initDriver():
    directory = pathlib.Path(__file__).parent.resolve()

    config = ConfigParser()
    config.read("config.ini")
    chromedriver = config["CHROME"]["chromedriverPath"]
    port = int(config["CHROME"]["chromePort"])

    options = Options()
    options.headless = True
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    if isPortInUse(port):
        driver = webdriver.Chrome(chromedriver, options=options)
    else:
        chromePath = config["CHROME"]["chromePath"]
        chromeUserDataDir = config["CHROME"]["chromeUserDataDir"]
        subprocess.run([
            chromePath, 
            f"--remote-debugging-port={port}", 
            f"--user-data-dir={chromeUserDataDir}"
        ])

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