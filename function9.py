# Import all necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import pandas as pd

# Load companies from CSV

path="dataset/company_list.csv"
def load_companies_from_csv(file_path=path):
    print(f"Loading companies from {file_path}")
    companies = pd.read_csv(path)
    if "company_name" not in companies.columns or "url" not in companies.columns:
        raise ValueError("CSV must contain 'Company' and 'Website' columns")
    return list(companies[["company_name", "url"]].itertuples(index=False, name=None))

# Setup browser
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

# Accept cookies
def accept_cookies(driver):
    cookie_locators = [
        (By.NAME, 'cookieAgree'),
        (By.CLASS_NAME, 'wscrOk'),
        (By.ID, 'onetrust-accept-btn-handler'),
        (By.CLASS_NAME, 'button.button--icon.button--icon'),
        (By.CLASS_NAME, 't_cm_ec_continue_button'),
        (By.XPATH, "//button[contains(., 'Accept')]"),
    ]
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        for by, selector in cookie_locators:
            try:
                btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                btn.click()
                return True
            except:
                continue
    except:
        pass
    return False

# Navigate to contact page
def navigate_to_contact_page(driver):
    contact_phrases = ["Contact", "Contact us", "Get in touch", "Reach us", "Contact me"]
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

# Extract contact info using better regex
def extract_contact_info(driver):
    print("🔍 Extracting contact information...")

    info = {"email": "Not found", "phone": "Not found", "address": "Not found"}

    # Keywords for identifying address blocks
    address_keywords = ["street", "road", "city", "PO Box", "London", "UK", "India", "US"]

    # Regex patterns
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_regex = r'(\+?\d[\s\-()]*\d{2,}[\s\-()]*\d{2,}[\s\-()]*\d{2,}[\s\-()]*\d{2,})'

    # Try finding near headers first
    header_texts = ["Contact Us", "Contact Information", "Global Headquarters", "Head Office", "Registered Office"]
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
                html = container.get_attribute('innerHTML')
                text = container.text.strip()

                emails = re.findall(email_regex, html)
                phones = re.findall(phone_regex, html)

                info["email"] = emails[0] if emails else info["email"]
                info["phone"] = phones[0].strip() if phones else info["phone"]
                info["address"] = text

                if info["email"] != "Not found":
                    return info
        except:
            continue

    # Try common class names
    contact_classes = ["contact-info", "contact-details", "address-block", "footer__text"]
    for cls in contact_classes:
        try:
            el = driver.find_element(By.CLASS_NAME, cls)
            html = el.get_attribute('innerHTML')
            text = el.text.strip()

            emails = re.findall(email_regex, html)
            phones = re.findall(phone_regex, html)

            info["email"] = emails[0] if emails else info["email"]
            info["phone"] = phones[0].strip() if phones else info["phone"]
            info["address"] = text
            if info["email"] != "Not found":
                return info
        except:
            continue

    # Fallback: scan body text
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.splitlines()
        for line in lines:
            line_clean = line.strip()
            if any(kw in line_clean.lower() for kw in address_keywords):
                info["address"] = line_clean
                break
    except:
        pass

    # Final fallback: scan full page source
    try:
        page_source = driver.page_source
        emails = re.findall(email_regex, page_source)
        phones = re.findall(phone_regex, page_source)

        info["email"] = emails[0] if emails else info["email"]
        info["phone"] = phones[0].strip() if phones else info["phone"]

        # Clean up short garbage phone numbers
        if info["phone"] != "Not found" and len(info["phone"]) < 6:
            info["phone"] = "Not found"

    except:
        pass

    return info

# Scrape one website
def scrape_website(company_name, url):
    driver = setup_driver()
    driver.get(url)

    print(f"\n🌐 Scraping: {company_name}")

    accept_cookies(driver)
    if not navigate_to_contact_page(driver):
        print("⚠️ Using homepage for contact info")

    contact_data = extract_contact_info(driver)

    driver.quit()
    return {
        "Company": company_name,
        "Website": url,
        "Email": contact_data["email"],
        "Phone": contact_data["phone"],
        "Address": contact_data["address"]
    }

# Main function
if __name__ == "__main__":
    companies = load_companies_from_csv("dataset/company_list.csv")
    all_results = []

    for name, url in companies:
        result = scrape_website(name, url)
        all_results.append(result)

    # Save to CSV
    df = pd.DataFrame(all_results)
    df.to_csv("contact_data_function9.csv", index=False, encoding="utf-8")
    df.to_excel("contact_data_function9.xlsx",index=False)
    print("\n✅ Data saved to contact_data.csv")