from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://www.saucedemo.com/")

    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inventory_list")))
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()

    badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
    assert badge == "1", f"Cart should have at least 1, current is {badge}"
    print("PASS: Add successfully.")

finally:
    driver.quit()
