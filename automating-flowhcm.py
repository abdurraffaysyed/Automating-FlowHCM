
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import logging
import signal
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)

# User credentials (for demonstration, replace these with actual env variables or a more secure method)
username = os.getenv("FLOWHCM_USERNAME")
password = os.getenv("FLOWHCM_PASSWORD")
waitingTime = os.getenv("WAITING_PERIOD")
if not username or not password:
    logging.error("Username or password environment variable not set")
    exit(1)

logging.info("Starting the script")

# Initialize WebDriver with ChromeDriverManager
options = Options()
# options.add_argument("--headless")  # Run in headless mode (optional)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, waitingTime)



def signal_handler(sig, frame):
    logging.info("Script interrupted by user")
    exit(0)

# Register the signal handler for graceful cleanup
signal.signal(signal.SIGINT, signal_handler)

def cleanupprocess(driver, wait):
    try:
        if element_exists(driver, By.CSS_SELECTOR, 'input.btn.btn-SignOut'):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.btn.btn-SignOut'))).click()
            time.sleep(5)
            logging.info("Signed out successfully")
        else:
            logging.error("Couldn't find the sign out button")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
    finally:
        driver.quit()
        logging.info("Closed the browser")

def log_in(driver, wait):
    try:
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "sign-in-btn1").click()
        logging.info("login successful")
        # Wait for the page to load completely
        time.sleep(5)

        # Attempt to click the sign-in or sign-back-in button
        if element_exists(driver, By.CSS_SELECTOR, 'input[value="Sign In"]'):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[value="Sign In"]'))).click()
            time.sleep(2)
        elif element_exists(driver, By.CSS_SELECTOR, 'input[value="Sign Back In"]'):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[value="Sign Back In"]'))).click()
            time.sleep(2)

    except TimeoutException as e:
        logging.error(f"Timeout during login process: {e}")
        logging.info("Please restart the script as retry hasn't been implemented for now")
        raise
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.info("Please restart the script")
        raise

def element_exists(driver, by, value):
    try:
        driver.find_element(by, value)
        return True
    except:
        return False

try:
    # Attempt to login
    logging.info("Attempting login...")
    driver.get("https://thinkdigitally.flowhcm.com/#/signin")
    log_in(driver, wait)

    # Keep the script running to avoid premature termination (if needed)
    print("Press Y to sign out: ")
    while True:
        x = input()
        if x == 'Y' or 'y':
            cleanupprocess(driver, wait)
            exit(0)
        else:
            print("Please enter the valid character")
            continue

except Exception as e:
    logging.error(f"An error occurred: {e}")
    
    exit(1)
