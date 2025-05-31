from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import numpy as np
import time
import re


path="dataset/company_w.csv"
# Remember -  we need company_name,website as header
#else it won't work
def load_companies_from_csv(file_path=path):
    print(f"Accessing Dataset at:  {file_path}")
    companies = pd.read_csv(path)
    if "company_name" not in companies.columns or "website" not in companies.columns:
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
            ("Jaguar Land Rover", "https://www.jaguarlandrover.com")
        ]
    return list(companies[["company_name", "website"]].itertuples(index=False, name=None))

#Setup Driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.cookies": 1,
        "profile.block_third_party_cookies": False
    })
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Cookies
def accept_cookies(driver):
    cookie_locators = [
        (By.NAME, 'cookieAgree'),
        (By.CLASS_NAME, 'wscrOk'),
        (By.ID, 'onetrust-accept-btn-handler'),
        (By.CLASS_NAME, 'button.button--icon.button--icon'),
        (By.CLASS_NAME, 't_cm_ec_continue_button'),
    ]
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        for by, selector in cookie_locators:
            try:
                btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                btn.click()
                print(f"Cookies accepted")
                return True
            except:
                continue
        print("No cookie")
    except:
        pass
    return False

# Exception for one website - diageo
def handle_diageo_age_verification(driver):
    if "diageo.com" in driver.current_url:
        try:
            year_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "age_select_year_of_birth"))
            )
            year_input.send_keys("1996")
            driver.find_element(By.ID, "age_confirm_btn").click()
            print("Diageo age verification")
        except:
            print("Diageo exception failed")

# Region
def select_region(driver):
    region_trigger_keywords = ["Global", "Region", "Location"]
    preferred_regions = ["India", "UK", "United Kingdom", "US", "United States"]

    for keyword in region_trigger_keywords:
        try:
            region_link = driver.find_element(By.PARTIAL_LINK_TEXT, keyword)
            region_link.click()
            time.sleep(2)
            break
        except NoSuchElementException:
            continue

    for region in preferred_regions:
        try:
            region_option = driver.find_element(By.PARTIAL_LINK_TEXT, region)
            region_option.click()
            time.sleep(3)
            return True
        except NoSuchElementException:
            continue

    return False

# Contact us
def navigate_to_contact_page(driver):
    contact_phrases = ["Contact", "Contacts", "Contact us", "Get in touch", "Reach us", "Contact me"]
    for phrase in contact_phrases:
        try:
            link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, phrase))
            )
            link.click()
            return True
        except:
            continue
    return False

# Access Info.
def extract_contact_info(driver):
    info = {"email": "Not found", "phone": "Not found", "address": "Not found"}
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_regex = r'(\+?\d[\s\-()]*\d{2,}[\s\-()]*\d{2,}[\s\-()]*\d{2,}[\s\-()]*\d{2,})'

    address_keywords = ["street", "road", "city", "PO Box", "London", "UK", "India", "US"]

    header_texts = ["Contact Us", "Contact Information", "Global Headquarters", "Head Office", "Registered Office"]

    def extract_from_container(container):
        html = container.get_attribute('innerHTML')
        text = container.text.strip()

        emails = re.findall(email_regex, html)
        phones = re.findall(phone_regex, html)

        # return {
        #     "company": company_name,
        #     "website": website,
        #     "email": emails[0] if emails else "Not found",
        #     "phone": phones[0].strip() if phones else "Not found",
        #     "address": text
        # }

    # headers
    for header_text in header_texts:
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
                result = extract_from_container(container)
                if result["email"] != "Not found":
                    return result
        except:
            continue

    # By class names
    contact_classes = ["contact-info", "contact-details", "address-block", "footer__text"]
    for cls in contact_classes:
        try:
            el = driver.find_element(By.CLASS_NAME, cls)
            result = extract_from_container(el)
            if result["email"] != "Not found":
                return result
        except:
            continue

    # body text
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.splitlines()
        for line in lines:
            line_clean = line.strip()
            if any(i in line_clean.lower() for i in address_keywords):
                info["address"] = line_clean
                print("address")
                break
    except:
        pass

    # full page
    try:
        page_source = driver.page_source
        emails = re.findall(email_regex, page_source)
        phones = re.findall(phone_regex, page_source)

        info["email"] = emails[0] if emails else info["email"]
        info["phone"] = phones[0].strip() if phones else info["phone"]
    except:
        pass

    return info

# Extract data
def scrape_website(company_name, website):


    driver = setup_driver()
    driver.get(website)

    accept_cookies(driver)
    handle_diageo_age_verification(driver)
    if not navigate_to_contact_page(driver):
        print("Homepage")
    contact_data = extract_contact_info(driver)

    # contact_data["Company"] = company_name
    # contact_data["Website"] = website

    driver.quit()
    return {
        "Company": company_name,
        "Website": website,
        "Email": contact_data["email"],
        "Phone": contact_data["phone"],
        "Address": contact_data["address"]
    }

#mian
if __name__ == "__main__":
    companies = load_companies_from_csv("dataset/company_w.csv")
    all_results = []

    for company_name, website in companies:
        print(f"\nScraping: {company_name} - {website}")
        result = scrape_website(company_name, website)

        all_results.append(result)
        # Result
        for key, value in result.items():
            print(f"{key + ':':<10} {value}")


    # Save final data to CSV and Excel
    df_output = pd.DataFrame(all_results)
    df_output.to_csv("output/contact_data.csv", index=False, encoding="utf-8")
    df_output.to_excel("output/contact_data.xlsx", index=False)

    print("\nData saved to contact_data.csv and contact_data.xlsx")
