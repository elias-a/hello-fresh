import pathlib
import subprocess
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class ChromeDriver:

    def __init__(self, configPath):
        self.config = ConfigParser()
        self.config.read(configPath)

        self.initDriver()

    @staticmethod
    def isPortOpen(port):
        completedProcess = subprocess.run(["lsof", f"-i:{port}"], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return completedProcess.returncode != 0

    def initDriver(self):
        directory = pathlib.Path(__file__).parent.resolve()

        chromedriver = self.config["CHROME"]["chromedriverPath"]
        self.chromePort = int(self.config["CHROME"]["chromePort"])

        options = Options()
        options.headless = True
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.chromePort}")

        if ChromeDriver.isPortOpen(self.chromePort):
            self.isNewProcess = True
            self.openChrome()
        else:
            self.isNewProcess = False

        self.driver = webdriver.Chrome(chromedriver, options=options)

    def openChrome(self):
        chromePath = self.config["CHROME"]["chromePath"]
        chromeUserDataDir = self.config["CHROME"]["chromeUserDataDir"]
        self.chromeProcess = subprocess.Popen([
            chromePath, 
            f"--remote-debugging-port={self.chromePort}", 
            f"--user-data-dir={chromeUserDataDir}"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def closeChrome(self):
        if self.isNewProcess:
            self.chromeProcess.terminate()
        
        self.driver.quit()