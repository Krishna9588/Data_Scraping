# Import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re
import pandas as pd

path = "../dataset/company_list.csv"
# Load companies from CSV
def load_companies_from_csv(file_path=path):
    print(f"📂 Loading companies from {file_path}")
    df = pd.read_csv(file_path)
    if "company_name" not in df.columns or "url" not in df.columns:
        raise ValueError("CSV must contain 'company_name' and 'url'")
    return list(df[["company_name", "url"]].itertuples(index=False, name=None))


# Setup browser
def setup_driver(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.cookies": 1,
        "profile.block_third_party_cookies": False
    })
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


# Accept cookies
def accept_cookies(driver):
    cookie_locators = [
        (By.NAME, 'cookieAgree'),
        (By.CLASS_NAME, 'wscrOk'),
        (By.ID, 'onetrust-accept-btn-handler'),
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
        print("❌ No cookie banner found")
    except Exception as e:
        pass
    return False


# Handle Diageo age gate
def handle_diageo_age_verification(driver):
    if "diageo.com" in driver.current_url:
        try:
            year_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "age_select_year_of_birth"))
            )
            year_input.send_keys("1996")
            driver.find_element(By.ID, "age_confirm_btn").click()
            print("✅ Diageo age gate passed")
            time.sleep(3)
            return True
        except:
            print("⚠️ Diageo age gate failed")
    return False


# Click search icon (for sites like Rolls-Royce)
def click_search_icon_if_present(driver):
    if "rolls-royce.com" in driver.current_url:
        try:
            search_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "Nav-search__button.icon-Icon_Search"))
            )
            search_icon.click()
            time.sleep(1)
            print("✅ Search icon clicked (Rolls-Royce)")
            return True
        except:
            print("❌ No search icon found (Rolls-Royce)")
    return False


# Navigate using internal search bar
def navigate_using_site_search(driver, base_url, tech_term):
    """
    Navigates to a page related to the given technology term.
    Returns final URL after search
    """
    print(f"\n🔍 Searching for '{tech_term}' on {base_url}")
    driver.get(base_url)
    time.sleep(2)

    # Accept cookies
    accept_cookies(driver)

    # Special case: Diageo
    if "diageo.com" in base_url:
        handle_diageo_age_verification(driver)

    # Custom strategies per website
    if "rolls-royce.com" in base_url:
        if click_search_icon_if_present(driver):
            search_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".search-query.search-txt.Nav-search__input.ui-autocomplete-input"))
            )
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            return driver.current_url

    elif "baesystems.com" in base_url:
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']"))
            )
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            return driver.current_url
        except:
            print("❌ BAE Systems search bar not found")

    elif "gsk.com" in base_url:
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "site-search__input"))
            )
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            return driver.current_url
        except:
            print("❌ GSK search bar not found")

    elif "bt.com" in base_url:
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "txtSearch"))
            )
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            return driver.current_url
        except:
            print("❌ BT search bar not found")

    elif "vodafone.com" in base_url:
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".searchBar__input"))
            )
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            return driver.current_url
        except:
            print("❌ Vodafone search bar not found")

    elif "jaguarlandrover.com" in base_url:
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "q"))
            )
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            return driver.current_url
        except:
            print("❌ Jaguar Land Rover search bar not found")

    # Fallback: Try finding any visible search input
    try:
        search_input = None
        search_locators = [
            (By.TAG_NAME, "input"), 
            (By.CLASS_NAME, "search"),
            (By.ID, "search"),
            (By.NAME, "q"),
            (By.NAME, "query"),
            (By.XPATH, "//input[@type='text' and contains(@placeholder, 'Search')]")
        ]

        for by, selector in search_locators:
            try:
                search_input = driver.find_element(by, selector)
                break
            except:
                continue

        if search_input:
            search_input.clear()
            search_input.send_keys(tech_term)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            print(f"📌 Searched for '{tech_term}' → {driver.current_url}")
            return driver.current_url
        else:
            print("❌ Could not find search bar — falling back to homepage")
            return base_url

    except Exception as e:
        print(f"⚠️ Error navigating via search bar: {e}")
        return base_url


# Detect technologies in current page
def detect_technologies(driver, tech_term):
    print(f"🔎 Scanning for {tech_term} tools...")

    html = driver.page_source
    text = driver.find_element(By.TAG_NAME, "body").text

    combined = html + text

    cloud_tools = ["AWS", "Azure", "GCP", "Amazon Web Services", "Microsoft Azure", "Google Cloud Platform"]
    mes_tools = ["Siemens Opcenter", "Rockwell FactoryTalk", "FactoryTalk", "Wonderware", "Preactor", "SIMATIC IT"]
    plm_tools = ["Teamcenter", "Windchill", "ENOVIA", "Aras Innovator", "Dassault ENOVIA"]

    def detect_match(tools, content):
        for tool in tools:
            if re.search(tool, content, re.IGNORECASE):
                return tool
        return "-"

    if tech_term == "cloud":
        return {"tool": detect_match(cloud_tools, combined), "source": driver.current_url}
    elif tech_term == "MES":
        return {"tool": detect_match(mes_tools, combined), "source": driver.current_url}
    elif tech_term == "PLM":
        return {"tool": detect_match(plm_tools, combined), "source": driver.current_url}
    else:
        return {"tool": "-", "source": driver.current_url}


# Scrape one company for all tech categories
def scrape_tech_website(company_name, url):
    print(f"\n🌐 Scraping Tech for: {company_name}")

    result = {
        "Company": company_name,
        "Website": url,
        "Cloud Tool Mentioned": "-",
        "Cloud Source URL": url,
        "MES Tool Mentioned": "-",
        "MES Source URL": url,
        "PLM Tool Mentioned": "-",
        "PLM Source URL": url
    }

    # --- CLOUD ---
    driver = setup_driver()
    driver.get(url)
    accept_cookies(driver)
    if "diageo.com" in url:
        handle_diageo_age_verification(driver)

    cloud_result = detect_technologies(driver, "cloud")
    result.update({
        "Cloud Tool Mentioned": cloud_result["tool"],
        "Cloud Source URL": cloud_result["source"]
    })
    driver.quit()

    # --- MES ---
    driver = setup_driver()
    driver.get(url)
    accept_cookies(driver)
    if "diageo.com" in url:
        handle_diageo_age_verification(driver)

    mes_result = detect_technologies(driver, "MES")
    result.update({
        "MES Tool Mentioned": mes_result["tool"],
        "MES Source URL": mes_result["source"]
    })
    driver.quit()

    # --- PLM ---
    driver = setup_driver()
    driver.get(url)
    accept_cookies(driver)
    if "diageo.com" in url:
        handle_diageo_age_verification(driver)

    plm_result = detect_technologies(driver, "PLM")
    result.update({
        "PLM Tool Mentioned": plm_result["tool"],
        "PLM Source URL": plm_result["source"]
    })
    driver.quit()

    return result


# Main function
def main():
    companies = load_companies_from_csv()

    all_results = []

    for idx, (name, url) in enumerate(companies):
        print(f"\n🚀 [{idx+1}/{len(companies)}] Detecting technologies for: {name}")
        result = scrape_tech_website(name, url)
        all_results.append(result)

        print("-" * 60)
        for key, value in result.items():
            print(f"{key + ':':<25} {value}")
        print("-" * 60)

    # Save results to file
    df = pd.DataFrame(all_results)
    df.to_csv("technology_detection.csv", index=False, encoding="utf-8")
    df.to_excel("technology_detection.xlsx", index=False)
    print("\n✅ Data saved to technology_detection.csv and .xlsx")


if __name__ == "__main__":
    main()