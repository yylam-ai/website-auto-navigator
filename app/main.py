from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from utils.utils import extract_data, check_paywall, are_all_buttons_clickable
from dotenv import load_dotenv
import os
import time
import csv
import math

load_dotenv()

IMAGE_DIR = os.getenv("IMGPATH")
SELENIUM_SERVER = os.getenv("SELENIUM_SERVER")

CSV_FILE_PATH = 'webpage_data_dict.csv'


def auto_progress(driver: webdriver.Remote, url):
    driver.get(url)
    driver.maximize_window()

    page=1
    website_data = []
    previous_state = None

    while True:
        scrolling = 1
        clickable_element = None
        progress_bar_detected = False
        
        time.sleep(1)
        
        data = extract_data(driver)
        website_data.append(data)

        screenshot_path = IMAGE_DIR + f'screenshot{page}_{scrolling}.png'

        driver.save_screenshot(screenshot_path)
        
        # Get total page height
        total_page_height = driver.execute_script("return document.body.scrollHeight;")

        while math.ceil(driver.execute_script("return window.pageYOffset;") + driver.execute_script("return window.innerHeight;")) < total_page_height:
            scrolling+=1

            # Scroll down by the specified number of pixels
            driver.execute_script(f"window.scrollBy(0, {1000});")

            screenshot_path = IMAGE_DIR + f'screenshot{page}_{scrolling}.png'

            # driver.save_screenshot(screenshot_path)

        # detect progress bar
        progress_bar = driver.find_elements(By.CSS_SELECTOR, '.progressbar-text')
        while progress_bar:
            progress_bar_detected = True
            time.sleep(1)
            progress_bar = driver.find_elements(By.CSS_SELECTOR, '.progressbar-text')
        if progress_bar_detected:
            continue

        # input_field = driver.find_elements(By.CLASS_NAME, 'cta-button')
        input_fields = driver.find_elements(By.CSS_SELECTOR, 'input')
        if input_fields:
            input_field = input_fields[0]
            input_field.send_keys("rando")
            
            if 'placeholder' in input_field.get_attribute('outerHTML'):
                placeholder_value = input_field.get_attribute('placeholder')
                if "email" in placeholder_value.lower():
                    input_field.send_keys("rando@fjamail.com")   

            data_cy  =  input_field.get_attribute('data-cy')
            if data_cy:   
                if 'input-CENTIMETER' in data_cy:
                    input_field.send_keys(180)  
                elif 'input-KILOGRAM' in data_cy:
                    if "ideal weight" in driver.find_element(By.TAG_NAME, "body").text:
                        input_field.send_keys(65)
                    else:
                        input_field.send_keys(80)
    
        
        # click radio button
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        if radio_buttons:
            for radio in radio_buttons:
                if radio.is_enabled() and radio.is_displayed():
                    radio.click()
                    break

        # click checkbox
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkboxes:
            checkboxes[0].click()


        # pick date
        calendar = driver.find_elements(By.CSS_SELECTOR, ".react-datepicker__day")
        if calendar:
            calendar[-1].click()

        # handle slider:
        sliders = driver.find_elements(By.CSS_SELECTOR, "[role='slider']")
        if sliders:
            move = ActionChains(driver)
            move.click_and_hold(sliders[0]).move_by_offset(90, 0).release().perform()


        # end program when there is paywall
        has_paywall =  check_paywall(driver)
        if has_paywall:
            print("detected paywall:", driver.current_url)
            break

        # progress to next page here
        # WebDriverWait(driver, 3).until(are_all_buttons_clickable)
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        all_clikable_url = driver.find_elements(By.TAG_NAME, "a")
        while not all_buttons and not all_clikable_url:
            time.sleep(1)
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            all_clikable_url = driver.find_elements(By.TAG_NAME, "a")

        else:
            filtered_buttons = [button for button in all_buttons if button.get_attribute("data-cy")!="back-button"]
            while filtered_buttons:
                new_state = driver.execute_script("return window.history.state")
                if new_state != previous_state:
                    previous_state = new_state
                    continue
                clickable_element = filtered_buttons.pop(0)

                # some buttons are not interactable
                try:
                    clickable_element.click()
                except:
                    pass
                time.sleep(0.5)
            
            if all_clikable_url:
                clikable_url = all_clikable_url[0]
                clikable_url.click()
                continue

                    
        page += 1
    
    # Write the data to the CSV file using DictWriter
    with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Url', 'Title', 'Description']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()  # Write the header
        writer.writerows(website_data)  # Write the data




def main():
    try:
        options = webdriver.ChromeOptions()
        driver = webdriver.Remote(
            command_executor=SELENIUM_SERVER, options=options
        )

        url = "https://start.thefabulous.co/onboarding/fab-initial-fb"
        # url = "https://www.noom.com/survey/email"
        # url = "https://www.noom.com/survey/weightLossGoal"

        auto_progress(driver, url)

        # driver.get(url) 
        # driver.maximize_window()
        # time.sleep(2)
        # input_field = driver.find_elements(By.CSS_SELECTOR, "test")
        # print(input_field)
        # input_field.send_keys("rando@edfmail.com")
        # btn = driver.find_element(By.TAG_NAME, "button")
        # print(btn.get_attribute("hello"))
        # btn.click()
        # time.sleep(2)
        


        # input_field = driver.find_element(By.CSS_SELECTOR, "input")
        # input_field.send_keys("June 24 2025")

        # slider = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "[role='slider']"))
        # )
        # move = ActionChains(driver)
        # move.click_and_hold(slider).move_by_offset(90, 0).release().perform()


        # time.sleep(2)

        driver.quit()

    except Exception as e:
        print("Exception:", e)
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()