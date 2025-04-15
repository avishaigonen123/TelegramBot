from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

# Set up headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Logging setup
log_filename = "check_timer.log"
now = datetime.now()
date_str = now.strftime("%B %d, %Y")

def write_log(message):
    with open(log_filename, "a") as log:
        log.write(f"[{date_str}] {message}\n")

try:
    # Login
    driver.get("https://client.webhostmost.com/login")
    email_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    email_field.send_keys("example@gmail.com")  # Replace with your actual email
    password_field.send_keys("password")  # Replace with your actual password
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)
    if "clientarea.php" not in driver.current_url:
        write_log("Login failed!")
        raise Exception("Login failed!")

    # Go to timer
    driver.get("https://client.webhostmost.com/clientarea.php")
    time.sleep(5)

    timer = driver.find_element(By.ID, "custom-timer")
    days = int(timer.find_element(By.ID, "timer-days").text)
    hours = int(timer.find_element(By.ID, "timer-hours").text)
    minutes = int(timer.find_element(By.ID, "timer-minutes").text)
    seconds = int(timer.find_element(By.ID, "timer-seconds").text)

    result = f"Time until suspension: {days}d {hours}h {minutes}m {seconds}s"
    print(result)

    write_log(f"Login successful. Extracted: {days} days, {minutes} minutes.")

except Exception as e:
    # write_log(f"Error: {str(e)}")
    write_log(f"Error !")

finally:
    driver.quit()
