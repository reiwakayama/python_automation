import ssl
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# Keep SSL unverified for urllib (if you use urllib later in the script)
ssl._create_default_https_context = ssl._create_unverified_context

def check_qatar_airways():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Comment out headless for now; headless is often detected and blocked
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = uc.Chrome(options=options)
        url = "https://www.qatarairways.com/en-us/search-award-flights.html?from=HKG&to=ATL&departure=2025-11-29&cabin=Business&adults=1"
        print(f"Attempting to load {url}")
        driver.get(url)

        time.sleep(5)

        # Mimic some user action - scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        print("✅ Page loaded.")
        print("Title:", driver.title)
        print("URL after loading:", driver.current_url)

    except WebDriverException as e:
        print(f"❌ Qatar Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    check_qatar_airways()
