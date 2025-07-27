import json
import sys
import time
import re
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

        try:
            star_rating_div = card.find_element(By.CSS_SELECTOR, "div[class^='star-rating']")
            rating_img = star_rating_div.find_element(By.TAG_NAME, "img")
            rating_alt_text = rating_img.get_attribute("alt")
            review_data["rating"] = extract_rating(rating_alt_text)
        except (NoSuchElementException, AttributeError):
            review_data["rating"] = None

        try:
            title_element = card.find_element(By.CSS_SELECTOR, "h2[class^='typography_heading']")
            review_data["title"] = title_element.text.strip()
        except NoSuchElementException:
            review_data["title"] = ""

        try:
            review_element = card.find_element(By.CSS_SELECTOR, "p[class^='typography_body']")
            review_data["review"] = review_element.text.strip()
        except NoSuchElementException:
            review_data["review"] = ""

        try:
            date_element = card.find_element(By.CSS_SELECTOR, "time")
            review_data["date"] = date_element.get_attribute("datetime")
        except NoSuchElementException:
            review_data["date"] = ""

        reviews_data.append(review_data)

    print(f"Scraped {len(reviews_data)} reviews from {url}")
    return reviews_data


def main():
    base_url = "https://www.trustpilot.com/review/choosemuse.com"

    max_pages = 1
    scrape_all = False

    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'all':
            scrape_all = True
            max_pages = float('inf')
        else:
            try:
                max_pages = int(sys.argv[1])
            except ValueError:
                print("Invalid max_pages value. Using default (1).")

    driver = setup_driver()
    all_reviews = []
    current_page = 1
    reached_404 = False

    try:
        print(f"Scraping page {current_page}...")
        page_data = scrape_page(driver, base_url)

        if page_data is None:
            reached_404 = True
        else:
            all_reviews.extend(page_data)

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

    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)

    print(f"Scraping complete. Scraped {len(all_reviews)} reviews across {current_page} pages.")
    print(f"Results saved to output.json")


if __name__ == "__main__":
    print("Usage: python script.py [max_pages]")
    print("max_pages can be a number or 'all'")
    print("If not specified, only the first page will be scraped.")
    main()