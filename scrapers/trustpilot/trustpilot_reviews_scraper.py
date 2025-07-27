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
    match = re.search(r"/review/([^/?\s]+)", base_url)
    if match:
        return match.group(1).strip("/")
    return "unknown-company"

def extract_rating(rating_text):
    # Try multiple patterns to extract rating
    patterns = [
        r'Rated (\d+)',
        r'(\d+) out of',
        r'(\d+) star',
        r'rating-(\d+)',
        r'stars-(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, rating_text, re.IGNORECASE)
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
        
        # Improved rating extraction with multiple approaches
        rating = None
        try:
            # Try multiple selectors for star rating
            rating_selectors = [
                "div[class*='star-rating'] img",
                "div[data-service-review-rating] img",
                "img[alt*='star']",
                "img[alt*='Rated']",
                "div[class*='rating'] img",
                "[class*='stars'] img",
                "div[data-service-review-rating]"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_element = card.find_element(By.CSS_SELECTOR, selector)
                    
                    # Try to get rating from alt text
                    if rating_element.tag_name == 'img':
                        alt_text = rating_element.get_attribute("alt")
                        if alt_text:
                            rating = extract_rating(alt_text)
                            if rating:
                                break
                    
                    # Try to get rating from data attributes
                    for attr in ['data-rating', 'data-stars', 'data-score']:
                        attr_value = rating_element.get_attribute(attr)
                        if attr_value and attr_value.isdigit():
                            rating = int(attr_value)
                            break
                    
                    if rating:
                        break
                        
                except NoSuchElementException:
                    continue
            
            # If still no rating found, try to find it in class names or other attributes
            if not rating:
                try:
                    # Look for elements with rating in class names
                    rating_elements = card.find_elements(By.CSS_SELECTOR, "[class*='rating'], [class*='star'], [data-rating]")
                    for elem in rating_elements:
                        # Check class names for rating info
                        class_name = elem.get_attribute("class") or ""
                        for i in range(1, 6):  # ratings 1-5
                            if f"rating-{i}" in class_name or f"stars-{i}" in class_name or f"star-{i}" in class_name:
                                rating = i
                                break
                        if rating:
                            break
                        
                        # Check data attributes
                        for attr in ['data-rating', 'data-stars', 'data-score']:
                            attr_value = elem.get_attribute(attr)
                            if attr_value and attr_value.isdigit():
                                rating = int(attr_value)
                                break
                        if rating:
                            break
                except:
                    pass
                    
        except Exception as e:
            print(f"Error extracting rating: {e}")
        
        review_data["rating"] = rating
        
        # Improved title extraction with multiple selectors
        title = ""
        try:
            title_selectors = [
                "h2[data-service-review-title-typography='true']",
                "h2[class^='typography_heading']",
                "h3[class^='typography_heading']",
                "h2[class*='heading']",
                "h3[class*='heading']",
                "div[data-service-review-title-typography='true']",
                "span[data-service-review-title-typography='true']",
                "[class*='review-title']",
                "[class*='reviewTitle']"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, selector)
                    potential_title = title_element.text.strip()
                    if potential_title and len(potential_title) > 2:
                        title = potential_title
                        break
                except NoSuchElementException:
                    continue
            
            # If no specific selector worked, look for any heading elements with substantial text
            if not title:
                try:
                    heading_elements = card.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
                    for element in heading_elements:
                        text = element.text.strip()
                        # Skip if it looks like metadata or very short
                        if (text and len(text) > 3 and len(text) < 200 and
                            not re.match(r'^\d+\s*(star|stars)', text.lower()) and
                            not re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)):
                            title = text
                            break
                except:
                    pass
                    
        except Exception as e:
            print(f"Error extracting title: {e}")
        
        review_data["title"] = title
        
        # Improved review text extraction with multiple selectors
        review_text = ""
        try:
            # Try multiple possible selectors for review content
            selectors = [
                "div[data-service-review-text-typography='true']",
                "p[data-service-review-text-typography='true']",
                "div[class*='review-content']",
                "p[class*='review-content']",
                "div[class^='typography_body-l']",
                "p[class^='typography_body-l']",
                "div[class^='typography_body']",
                "p[class^='typography_body']",
                "span[class*='typography_body']"
            ]
            
            for selector in selectors:
                try:
                    review_element = card.find_element(By.CSS_SELECTOR, selector)
                    potential_text = review_element.text.strip()
                    # Check if this looks like actual review content (not just metadata)
                    if potential_text and len(potential_text) > 10:
                        review_text = potential_text
                        break
                except NoSuchElementException:
                    continue
            
            # If no specific selector worked, try to find any text content in the card
            if not review_text:
                try:
                    # Look for any div or p with substantial text content
                    text_elements = card.find_elements(By.CSS_SELECTOR, "div, p")
                    for element in text_elements:
                        text = element.text.strip()
                        # Skip elements that are likely metadata (short text, dates, etc.)
                        if (text and len(text) > 20 and 
                            not re.match(r'^\d+\s*(star|stars|out of)', text.lower()) and
                            not re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text) and
                            'verified' not in text.lower() and
                            'helpful' not in text.lower()):
                            review_text = text
                            break
                except:
                    pass
                    
        except Exception as e:
            print(f"Error extracting review text: {e}")
        
        review_data["review"] = review_text
        
        try:
            date_element = card.find_element(By.CSS_SELECTOR, "time")
            review_data["date"] = date_element.get_attribute("datetime")
        except NoSuchElementException:
            review_data["date"] = ""
        reviews_data.append(review_data)
    print(f"Scraped {len(reviews_data)} reviews from {url}")    
    return reviews_data

def main():
    base_url = input("copy-paste the trustpilot review url (eg --> https://www.trustpilot.com/review/choosemuse.com): ").strip() # --- ensure URL is valid
    while not base_url:
        base_url = input("Base URL cannot be empty. Please enter a valid URL: ").strip()
    input_pages = input("Please enter how many pages you want to query (or 'all'): ").strip().lower()
    if input_pages == 'all':
        max_pages = float('inf')
        scrape_all = True
    else:
        scrape_all = False
        try:
            max_pages = int(input_pages)
        except ValueError:
            print("invalid number of pages provided --> defaulting to 1 page...")
            max_pages = 1
    company_name = extract_company_name(base_url)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"
    output_filename = f"{company_name}_trustpilot_reviews_{timestamp}.json"
    driver = setup_driver()
    all_reviews = []
    current_page = 1
    reached_404 = False
    try:
        print(f"scraping page {current_page}...")
        page_data = scrape_page(driver, base_url)
        if page_data is None:
            reached_404 = True
        else:
            all_reviews.extend(page_data)
        while not reached_404 and current_page < max_pages:
            current_page += 1
            next_page_url = f"{base_url}{'?' if '?' not in base_url else '&'}page={current_page}"
            print(f"scraping page {current_page}...")
            page_data = scrape_page(driver, next_page_url)
            if page_data is None:
                reached_404 = True
                break
            all_reviews.extend(page_data)
            time.sleep(2)
    finally:
        driver.quit()
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)
    if scrape_all and not reached_404:
        print("scraping complete (scraped until no more pages found).")
    else:
        pages_scraped = current_page if not reached_404 else current_page - 1
        print(f"query complete... queried {len(all_reviews)} reviews across {pages_scraped} page(s).")
    print(f"results saved to {output_filename}.")

if __name__ == "__main__":
    main()