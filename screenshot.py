# Get screenshot of open webpage

from PIL import Image
from selenium import webdriver
driver = webdriver.Chrome (r"C:\Users\Admin\chromedriver.exe")
driver.get("https://www.reimorikawa.com")
driver.save_screenshot("image.png")
image = Image.open("image.png")
image.show()
