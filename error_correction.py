# Import all necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import pandas as pd

# List of companies (you can add more if needed)
companies = [
    ("Rolls-Royce Holdings plc", "https://www.rolls-royce.com"),
    ("BAE Systems plc", "https://www.baesystems.com"),
    ("GlaxoSmithKline plc (GSK)", "https://www.gsk.com"),
    ("Unilever plc", "https://www.unilever.com"),
    ("AstraZeneca plc", "https://www.astrazeneca.com"),
    ("BT Group plc", "https://www.bt.com"),
    ("Tesco plc", "https://www.tescoplc.com"),
    ("Diageo plc", "https://www.diageo.com"),
    ("Vodafone Group plc", "https://www.vodafone.com"),
    ("Jaguar Land Rover (subsidiary of TATA)", "https://www.jaguarlandrover.com")
]

# Setup
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")

    # Allow cookies by default
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.cookies": 1,
        "profile.block_third_party_cookies": False
    })

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Cookies
def accept_cookies(driver, timeout=5):

    cookie_locators = [
        # tag, name, id from all 10 websites.
        (By.NAME, 'cookieAgree'),
        (By.CLASS_NAME, 'wscrOk'),
        (By.ID, 'onetrust-accept-btn-handler'),
        (By.ID, 'preferences_prompt_submit'),
        (By.CLASS_NAME, 'button.button--icon.button--icon'),
        (By.CLASS_NAME, 't_cm_ec_continue_button'),
    ]

    try:
        # Wait for any element on the page to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Try each known cookie button selector
        for by, selector in cookie_locators:
            try:
                # Wait for the cookie element to be clickable
                cookie_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                cookie_btn.click()
                print(f"Cookie accepted using: {by}='{selector}'")
                return True
            except (TimeoutException, NoSuchElementException):
                continue  # Try next locator

        print("No cookie")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Special case diageo age verification - 1996
def handle_diageo_age_verification(driver):
    try:
        year_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "age_select_year_of_birth"))
        )
        year_input.send_keys("1996")
        time.sleep(2)  # Small delay before clicking confirm
        driver.find_element(By.ID, "age_confirm_btn").click()
        print("verified.")
        time.sleep(3)  # Allow content to load after confirmation
        return True
    except Exception as e:
        print(f"failed: {e}")
        return False

# Region Toggle
def select_region(driver):

    region_trigger_keywords = ["Global", "GLOBAL", "Region", "REGION", "Location", "LOCATION"]
    preferred_regions = ["India", "INDIA", "IN", "UK", "United Kingdom", "US", "United States"]

    region_trigger_clicked = False
    for keyword in region_trigger_keywords:
        try:
            region_link = driver.find_element(By.PARTIAL_LINK_TEXT, keyword)
            region_link.click()
            print(f"Region : '{keyword}'")
            time.sleep(2)
            region_trigger_clicked = True
            break
        except NoSuchElementException:
            continue

    if not region_trigger_clicked:
        print("No region found.")
        return False

    for region in preferred_regions:
        try:
            region_option = driver.find_element(By.PARTIAL_LINK_TEXT, region)
            region_option.click()
            print(f"Selected region: '{region}'")
            time.sleep(3)
            return True
        except NoSuchElementException:
            continue

    return True

# Contact us Page
def navigate_to_contact_page(driver):
    contact_phrases = [
        (By.PARTIAL_LINK_TEXT, "Contact"),
        (By.PARTIAL_LINK_TEXT, "Contacts"),
        (By.PARTIAL_LINK_TEXT, "Contact us"),
        (By.PARTIAL_LINK_TEXT, "Contact BT"),
        (By.PARTIAL_LINK_TEXT, "Get in touch"),
        (By.PARTIAL_LINK_TEXT, "Reach us"),
        (By.PARTIAL_LINK_TEXT, "Contact me"),
        (By.ID, "dg_TERMS_OF_SALE"),
    ]

    main_window = driver.current_window_handle
    original_tabs = driver.window_handles

    for by, phrase in contact_phrases:
        try:
            contact_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by, phrase))
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_link)
            time.sleep(0.5)

            try:
                contact_link.click()
            except Exception:
                driver.execute_script("arguments[0].click();", contact_link)

            print(f"Contact found: '{phrase}'")

            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > len(original_tabs))

            for tab in driver.window_handles:
                if tab != main_window:
                    driver.switch_to.window(tab)
                    print("new tab.")
                    time.sleep(2)
                    return True

        except (TimeoutException, NoSuchElementException):
            continue
    return False

# Contact Info

def extract_contact_info(driver):

    info = {
        "email": "Not found",
        "phone": "Not found",
        "address": "Not found"
    }

    address_keywords = [
        "street", "road", "block", "london", "india", "united states", "us", "england",
        "city", "park", "near", "east", "west", "mumbai", "new delhi"
    ]

    header_patterns = [
        "Global headquarters", "Head office", "Registered office", "Corporate address",
        "Contact information", "Get in touch", "Contact details", "Contact Us",
        "T:", "Tel:", "Phone:"
    ]

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_regex = r'(\+?\d[\s\-()]*\d{2,}[\s\-()]*\d{2,}[\s\-()]*\d{2,}[\s\-()]*\d{2,})'

    def extract_info_from_container(container):
        contact_html = container.get_attribute('innerHTML')
        contact_text = container.text.strip()

        emails = re.findall(email_regex, contact_html)
        phones = re.findall(phone_regex, contact_html)

        return {
            "email": emails[0] if emails else "Not found",
            "phone": phones[0].strip() if phones else "Not found",
            "address": contact_text
        }

    def find_contact_info_by_header(header_text):
        try:
            header = driver.find_element(
                By.XPATH,
                f"//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{header_text.lower()}')] | "
                f"//h3[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{header_text.lower()}')]"
            )

            container = None
            try:
                container = header.find_element(By.XPATH, "./following-sibling::*[1]")
            except:
                try:
                    container = header.find_element(By.XPATH, "./parent::*")
                except:
                    pass

            if container:
                return extract_info_from_container(container)
        except:
            return None
        return None

    # Try known headers first
    for header in header_patterns:
        result = find_contact_info_by_header(header)
        if result and result["email"] != "Not found":
            info.update(result)
            print(f"header: {header}")
            return info

    # Try common class names
    contact_classes = ["contact-info", "contact-details", "address-block"]
    for cls in contact_classes:
        try:
            elements = driver.find_elements(By.CLASS_NAME, cls)
            for el in elements:
                result = extract_info_from_container(el)
                if result["email"] != "Not found":
                    info.update(result)
                    print(f"class: {cls}")
                    return info
        except Exception as e:
            continue

    # Fallback: scan full page source
    try:
        page_text = driver.page_source

        # Email fallback
        emails = re.findall(email_regex, page_text)
        if emails:
            info["email"] = emails[0]

        # Phone fallback
        phones = re.findall(phone_regex, page_text)
        if phones:
            info["phone"] = phones[0].strip()

        # Address fallback
        lines = page_text.splitlines()
        for line in lines:
            line_text = line.strip().lower()
            if any(kw in line_text for kw in address_keywords):
                info["address"] = line.strip()
                return info

    except Exception as e:
        print(f"Error: {e}")

    return info


def main():

    # Testing all function for Rools Royce  at 0 index.
    test_company = companies[0]
    company_name, website_url = test_company

    print(f"{company_name} - {website_url}")

    print("setup_driver()...")
    driver = setup_driver()
    driver.get(website_url)
    print("Driver checked.\n")

    print(f"driver.get({website_url})...")
    driver.get(website_url)
    print("Page loaded.\n")

    print("accept_cookies(driver)...")
    accept_cookies(driver)
    print("Cookies - (or not found).\n")

    print(f"handle_diageo_age_verification(driver)...")
    handle_diageo_age_verification(driver)
    print("Age - probelm - special case.\n")

    print(" select_region(driver)...")
    select_region(driver)
    print("Region - problem.")

    print("navigate_to_contact_page(driver)...")
    navigate_to_contact_page(driver)
    print("Contact Page.")

    print("extract_contact_info(driver)...")
    contact_data = extract_contact_info(driver)

    print("\n Contact Info:")
    print("----")
    for key, value in contact_data.items():
        print(f"{key + ':':<10} {value}")
    print("----")

    driver.quit()

# Problem after navigate to contact page