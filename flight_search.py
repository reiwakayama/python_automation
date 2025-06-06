import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                      WebDriverException,
                                      NoSuchElementException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from urllib3.exceptions import ReadTimeoutError

# ===== CONFIGURATION =====
ORIGIN = "HKG"  # Departure airport
DESTINATION = "ATL"  # Destination airport
DATE = "2025-11-29"  # Format: YYYY-MM-DD
HEADLESS = True  # Run browser in background
MAX_RETRIES = 3  # Retry failed attempts
DELAY_BETWEEN_AIRLINES = 5  # Seconds
PAGE_LOAD_TIMEOUT = 60  # Seconds

# ===== SETUP DRIVER =====
def setup_driver():
    options = webdriver.ChromeOptions()
    
    if HEADLESS:
        options.add_argument("--headless=new")  # New headless mode
        options.add_argument("--disable-gpu")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Anti-detection settings
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Random User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Configure ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set timeouts
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(10)
    
    # Mask Selenium detection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    return driver

# ===== SAFE PAGE LOAD =====
def safe_get(driver, url, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1} to load {url}")
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            driver.get(url)
            
            # Wait for page to fully load
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
            
        except (TimeoutException, WebDriverException, ReadTimeoutError) as e:
            print(f"⚠️ Page load failed (Attempt {attempt + 1}): {str(e)}")
            if attempt == retries - 1:
                return False
            time.sleep(random.uniform(2, 5))
            
            # Try refreshing
            try:
                driver.refresh()
            except:
                pass
    return False

# ===== AIRLINE SCRAPERS =====
def check_british_airways(driver):
    print("\n🔍 Checking British Airways...")
    url = f"https://www.britishairways.com/travel/book/public/en_us#/awardflight?origin={ORIGIN}&destination={DESTINATION}&outboundDate={DATE}&cabin=Business&adults=1"
    results = []
    
    try:
        if not safe_get(driver, url):
            print("❌ Failed to load BA page")
            return results
        
        # Wait for dynamic content
        time.sleep(5)
        
        # Scroll to trigger loading
        for _ in range(3):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)
        
        # JavaScript extraction as primary method
        flights_js = """
        var results = [];
        var containers = document.querySelectorAll('div.flight-info-container');
        
        containers.forEach(container => {
            try {
                var flight = container.querySelector('span.flight-number')?.innerText || 'N/A';
                var departure = container.querySelector('span.departure-time')?.innerText || 'N/A';
                var arrival = container.querySelector('span.arrival-time')?.innerText || 'N/A';
                var availability = container.querySelector('div.availability')?.innerText || 'N/A';
                
                results.push({
                    airline: 'British Airways',
                    flight: flight,
                    departure: departure,
                    arrival: arrival,
                    availability: availability
                });
            } catch(e) {}
        });
        
        return results;
        """
        
        results = driver.execute_script(flights_js)
        
        # Fallback to Selenium if JS fails
        if not results:
            containers = driver.find_elements(By.CSS_SELECTOR, "div.flight-info-container")
            for container in containers:
                try:
                    results.append({
                        "airline": "British Airways",
                        "flight": container.find_element(By.CSS_SELECTOR, "span.flight-number").text,
                        "departure": container.find_element(By.CSS_SELECTOR, "span.departure-time").text,
                        "arrival": container.find_element(By.CSS_SELECTOR, "span.arrival-time").text,
                        "availability": container.find_element(By.CSS_SELECTOR, "div.availability").text
                    })
                except:
                    continue
        
        return results
        
    except Exception as e:
        print(f"❌ BA Scraping Error: {str(e)}")
        return results

def check_qatar_airways(driver):
    print("\n🔍 Checking Qatar Airways (via form submission)...")
    results = []

    try:
        driver.get("https://www.qatarairways.com/en-us/Privilege-Club/award-flight-booking.html")
        
        # Wait for form to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "mat-input-0"))  # Origin field
        )

        # Origin
        origin_input = driver.find_element(By.ID, "mat-input-0")
        origin_input.clear()
        origin_input.send_keys(ORIGIN)
        time.sleep(1)
        origin_input.send_keys(Keys.DOWN, Keys.RETURN)

        # Destination
        dest_input = driver.find_element(By.ID, "mat-input-1")
        dest_input.clear()
        dest_input.send_keys(DESTINATION)
        time.sleep(1)
        dest_input.send_keys(Keys.DOWN, Keys.RETURN)

        # Departure date
        date_input = driver.find_element(By.ID, "mat-input-2")
        date_input.clear()
        date_input.send_keys(DATE)
        date_input.send_keys(Keys.RETURN)

        # Cabin class (assumes Business pre-selected)
        # You can modify dropdown selection here if needed

        # Click Search button
        search_button = driver.find_element(By.CSS_SELECTOR, "button.qr-primary-button")
        search_button.click()

        # Wait for results
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.flight-card"))
        )

        time.sleep(3)

        # Extract flight data
        cards = driver.find_elements(By.CSS_SELECTOR, "div.flight-card")
        for card in cards:
            try:
                flight_no = card.find_element(By.CSS_SELECTOR, "span.flight-no").text
                departure = card.find_element(By.CSS_SELECTOR, "span.departure").text
                arrival = card.find_element(By.CSS_SELECTOR, "span.arrival").text
                availability = card.find_element(By.CSS_SELECTOR, "div.seat-availability").text
                results.append({
                    "airline": "Qatar Airways",
                    "flight": flight_no,
                    "departure": departure,
                    "arrival": arrival,
                    "availability": availability
                })
            except NoSuchElementException:
                continue

        return results

    except Exception as e:
        print(f"❌ Qatar Airways Error: {str(e)}")
        return results

def check_singapore_airlines(driver):
    print("\n🔍 Checking Singapore Airlines...")
    url = f"https://www.singaporeair.com/en_UK/us/home#/book/bookflight/awardflight?origin={ORIGIN}&destination={DESTINATION}&departureDate={DATE}&cabin=Business&adults=1"
    results = []
    
    try:
        if not safe_get(driver, url):
            print("❌ Failed to load Singapore Airlines page")
            return results
        
        # Handle cookie consent
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "cookieAgreementBtn"))
            ).click()
        except:
            pass
        
        # Wait for flight results
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.flight-segment"))
        )
        
        # Extract data
        segments = driver.find_elements(By.CSS_SELECTOR, "div.flight-segment")
        for segment in segments:
            try:
                results.append({
                    "airline": "Singapore Airlines",
                    "flight": segment.find_element(By.CSS_SELECTOR, "span.flight-no").text,
                    "departure": segment.find_element(By.CSS_SELECTOR, "span.depart-time").text,
                    "arrival": segment.find_element(By.CSS_SELECTOR, "span.arrival-time").text,
                    "availability": segment.find_element(By.CSS_SELECTOR, "div.availability-status").text
                })
            except NoSuchElementException:
                continue
                
        return results
        
    except Exception as e:
        print(f"❌ Singapore Airlines Error: {str(e)}")
        return results

def check_cathay_pacific(driver):
    print("\n🔍 Checking Cathay Pacific...")
    url = f"https://www.cathaypacific.com/booking/{ORIGIN}/{DESTINATION}/{DATE}/1/0/0/Business"
    results = []
    
    try:
        if not safe_get(driver, url):
            print("❌ Failed to load Cathay Pacific page")
            return results
        
        # Wait for flight cards
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "flight-card"))
        )
        
        # Scroll to load all flights
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(2)
        
        # Extract flight data
        cards = driver.find_elements(By.CLASS_NAME, "flight-card")
        for card in cards:
            try:
                results.append({
                    "airline": "Cathay Pacific",
                    "flight": card.find_element(By.CLASS_NAME, "flight-number").text,
                    "departure": card.find_element(By.CSS_SELECTOR, "span.departure-time").text,
                    "arrival": card.find_element(By.CSS_SELECTOR, "span.arrival-time").text,
                    "availability": card.find_element(By.CLASS_NAME, "availability").text
                })
            except NoSuchElementException:
                continue
                
        return results
        
    except Exception as e:
        print(f"❌ Cathay Pacific Error: {str(e)}")
        return results

# ===== MAIN EXECUTION =====
def main():
    print("\n🚀 Starting Qatar Airways Only Test...")
    
    driver = None
    try:
        driver = setup_driver()
        results = check_qatar_airways(driver)
        
        if results:
            df = pd.DataFrame(results)
            print("\n📊 Qatar Airways Results:")
            print(df.to_markdown())
        else:
            print("❌ No Qatar Airways results.")
    
    finally:
        if driver:
            driver.quit()
        print("\n✅ Test completed.")

if __name__ == "__main__":
    main()
