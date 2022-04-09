import sys
import os
import signal
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
        chromedriver = self.config["CHROME"]["chromedriverPath"]
        self.chromePort = int(self.config["CHROME"]["chromePort"])

        options = Options()
        options.headless = True
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.chromePort}")

        if ChromeDriver.isPortOpen(self.chromePort):
            self.openChrome()
        else:
            print(f"Port {self.chromePort} is taken")
            sys.exit(1)

        self.driver = webdriver.Chrome(chromedriver, options=options)

    def openChrome(self):
        chromePath = self.config["CHROME"]["chromePath"]
        chromeUserDataDir = self.config["CHROME"]["chromeUserDataDir"]
        self.chromeProcess = subprocess.Popen([
            f"{pathlib.Path(__file__).parent.resolve()}/start_chrome.sh",
            chromePath,
            str(self.chromePort),
            chromeUserDataDir
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)

    def closeChrome(self):
        os.killpg(os.getpgid(self.chromeProcess.pid), signal.SIGTERM)
        self.driver.quit()