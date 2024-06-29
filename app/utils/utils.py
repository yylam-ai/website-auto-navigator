from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

import re


def check_paywall(driver: webdriver.Remote):

    overlay_detected = False
    #TODO: enahnce overlay detection to target keyword
    # overlays = driver.find_elements(By.CSS_SELECTOR, "[class*='overlay'], [class*='modal'], [id*='overlay'], [id*='modal']")
    # if overlays:
    #     overlay_detected = True

    # Check for redirect patterns
    current_url = driver.current_url
    if "subscribe" in current_url or "login" in current_url:
        overlay_detected = True

    # Check for hidden main content
    content_hidden = False

    # Check for paywall keywords in the body text
    body_text = driver.find_element(By.TAG_NAME, "body").text
    paywall_keywords = ["subscribe", "payment", "pay", "billed", "paywall", "login to continue", "subscribe to read"]

    for keyword in paywall_keywords:
        content_hidden = re.search(rf'\b{re.escape(keyword)}\b', body_text.lower(), re.IGNORECASE)
        if content_hidden:
            break
    # if any(keyword in body_text.lower() for keyword in paywall_keywords):
    #     content_hidden = True


    # Conclusion
    if overlay_detected or content_hidden:
        return True
    else:
        return False
    
def extract_data(driver: webdriver.Remote):
    current_url = driver.current_url
    title = driver.title

    try:
        meta_description = driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
        description_content =  meta_description.get_attribute("content")
    except Exception as e:
        description_content = ""

    return {
        "Url": current_url,
        "Title": title,
        "Description": description_content
    }

def are_all_buttons_clickable(driver):
    """
    Custom wait condition to check if all button elements are clickable.
    """
    try:
        # Find all button elements
        all_buttons = driver.find_elements(By.TAG_NAME, "button")

        # If no buttons found, we consider them not ready yet
        if not all_buttons:
            return False

        # Check if each button is clickable
        for button in all_buttons:
            # Use WebDriverWait to ensure each button is clickable
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(button))

        # If all buttons are clickable, return True
        return True
    except TimeoutException:
        # If any button is not clickable within the timeout, return False
        return False
