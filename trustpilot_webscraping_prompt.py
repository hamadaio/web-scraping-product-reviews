import json
import sys
import time
import re
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_company_name(base_url):
    """
    Extracts the portion after '/review/' in the URL (before the next slash or query).
    Example:
        base_url = 'https://www.trustpilot.com/review/choosemuse.com'
        returns 'choosemuse.com'
    """
    match = re.search(r"/review/([^/?\s]+)", base_url)
    if match:
        return match.group(1).strip("/")
    return "unknown-company"

def extract_rating(rating_text):
    match = re.search(r'Rated (\d+)', rating_text)
    if match:
        return int(match.group(1))
    return None

def scrape_page(driver, url):
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class^='styles_wrapper'][data-reviews-list-start='true']"))
        )
    except TimeoutException:
        # Check if the page is a 404
        try:
            driver.find_element(By.CSS_SELECTOR, "div[class^='errors_error404']")
            print(f"Reached a 404 page at: {url}")
            return None
        except NoSuchElementException:
            print(f"Timeout waiting for reviews list at: {url}")
            return []

    review_cards = driver.find_elements(By.CSS_SELECTOR, "div[class^='styles_cardWrapper']")

    reviews_data = []
    for card in review_cards:
        review_data = {}

        # Rating
        try:
            star_rating_div = card.find_element(By.CSS_SELECTOR, "div[class^='star-rating']")
            rating_img = star_rating_div.find_element(By.TAG_NAME, "img")
            rating_alt_text = rating_img.get_attribute("alt")
            review_data["rating"] = extract_rating(rating_alt_text)
        except (NoSuchElementException, AttributeError):
            review_data["rating"] = None

        # Title
        try:
            title_element = card.find_element(By.CSS_SELECTOR, "h2[class^='typography_heading']")
            review_data["title"] = title_element.text.strip()
        except NoSuchElementException:
            review_data["title"] = ""

        # Review
        try:
            review_element = card.find_element(By.CSS_SELECTOR, "p[class^='typography_body']")
            review_data["review"] = review_element.text.strip()
        except NoSuchElementException:
            review_data["review"] = ""

        # Date
        try:
            date_element = card.find_element(By.CSS_SELECTOR, "time")
            review_data["date"] = date_element.get_attribute("datetime")
        except NoSuchElementException:
            review_data["date"] = ""

        reviews_data.append(review_data)

    print(f"Scraped {len(reviews_data)} reviews from {url}")
    return reviews_data

def main():
    # Prompt user for the base URL
    base_url = input("Please enter the base URL (e.g., https://www.trustpilot.com/review/[company_name].com): ").strip()
    while not base_url:
        base_url = input("Base URL cannot be empty. Please enter a valid URL: ").strip()

    # Prompt user for how many pages to scrape or 'all'
    input_pages = input("Please enter how many pages you want to scrape (or 'all'): ").strip().lower()
    if input_pages == 'all':
        max_pages = float('inf')
        scrape_all = True
    else:
        scrape_all = False
        try:
            max_pages = int(input_pages)
        except ValueError:
            print("Invalid number of pages provided. Defaulting to 1 page.")
            max_pages = 1

    # Extract the company name from the base URL
    company_name = extract_company_name(base_url)

    # Generate timestamp in the format: 2025-03-22T23:46:46.000Z
    # Using current UTC time (timezone-aware).
    # NOTE: If you are on Windows, replace ':' in the filename if needed.
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"

    # Build the file name
    output_filename = f"{company_name}_trustpilot_reviews_{timestamp}.json"

    driver = setup_driver()
    all_reviews = []
    current_page = 1
    reached_404 = False

    try:
        # Scrape the first page
        print(f"Scraping page {current_page}...")
        page_data = scrape_page(driver, base_url)

        if page_data is None:
            reached_404 = True
        else:
            all_reviews.extend(page_data)

        # Scrape subsequent pages
        while not reached_404 and current_page < max_pages:
            current_page += 1
            next_page_url = f"{base_url}{'?' if '?' not in base_url else '&'}page={current_page}"

            print(f"Scraping page {current_page}...")
            page_data = scrape_page(driver, next_page_url)

            if page_data is None:
                reached_404 = True
                break

            all_reviews.extend(page_data)
            time.sleep(2)

    finally:
        driver.quit()

    # Write results to JSON using the company-specific, time-stamped filename
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)

    if scrape_all and not reached_404:
        print("Scraping complete (scraped until no more pages found).")
    else:
        pages_scraped = current_page if not reached_404 else current_page - 1
        print(f"Scraping complete. Scraped {len(all_reviews)} reviews across {pages_scraped} page(s).")

    print(f"Results saved to {output_filename}.")

if __name__ == "__main__":
    main()