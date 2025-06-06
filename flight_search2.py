from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 20)

driver.get("https://www.qatarairways.com/en-us/book.html")

# Accept cookies if present
try:
    cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "cookie-accept-all")))
    cookie_btn.click()
    print("Accepted cookies")
except:
    print("No cookie banner detected")

def input_airport(label_text, airport_code):
    print(f"Inputting {airport_code} into field labeled '{label_text}'")

    mat_label = wait.until(EC.presence_of_element_located(
        (By.XPATH, f'//mat-label[text()="{label_text}"]')
    ))
    mat_form_field = mat_label.find_element(By.XPATH, "./ancestor::mat-form-field")
    input_el = mat_form_field.find_element(By.CSS_SELECTOR, 'input[aria-label="Airport autocomplete"]')

    input_el.click()
    input_el.clear()
    input_el.send_keys(airport_code)

    options = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'mat-option')))
    if options:
        options[0].click()
        print(f"Selected {airport_code} for {label_text}")
    else:
        print(f"No autocomplete options found for {label_text}")

input_airport("From", "DOH")
input_airport("To", "LHR")

time.sleep(5)
driver.quit()
