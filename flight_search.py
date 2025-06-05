import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_qatar_airways():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Comment headless to reduce detection risk
    # options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    driver = uc.Chrome(options=options)

    try:
        driver.get("https://www.qatarairways.com/en-us/homepage.html")
        wait = WebDriverWait(driver, 20)

        # Wait for search form to load (example, change selector if needed)
        wait.until(EC.presence_of_element_located((By.ID, "search-flight-from")))

        # Fill "From" airport
        from_input = driver.find_element(By.ID, "search-flight-from")
        from_input.clear()
        from_input.send_keys("HKG")

        # Fill "To" airport
        to_input = driver.find_element(By.ID, "search-flight-to")
        to_input.clear()
        to_input.send_keys("ATL")

        # Fill departure date
        dep_input = driver.find_element(By.ID, "search-flight-departure-date")
        dep_input.clear()
        dep_input.send_keys("29/11/2025")  # format may need adjustment

        # Select cabin class (Business)
        cabin_select = driver.find_element(By.ID, "search-flight-cabin-class")
        cabin_select.click()
        # Choose Business option - this might require specific interaction

        # Submit the search form - find and click search button
        search_button = driver.find_element(By.ID, "search-flight-submit")
        search_button.click()

        # Wait for results page or confirmation element
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results-container")))

        print("✅ Search results loaded.")
        print("Title:", driver.title)
        print("URL:", driver.current_url)

    except Exception as e:
        print("❌ Qatar Error:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    check_qatar_airways()
