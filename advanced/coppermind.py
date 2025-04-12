import os
import time
import re
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Base URLs and directories
BASE_URL = "https://coppermind.net"
ALL_PAGES_URL = f"{BASE_URL}/wiki/Special:AllPages"
DEST_DIR = "coppermind_sorted"  # Folder where categorized files will be saved

# Create the destination directory if it doesn't exist.
os.makedirs(DEST_DIR, exist_ok=True)

def sanitize_filename(name):
    """Remove characters that are not allowed in filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_driver():
    """Set up and return a Selenium Chrome driver."""
    options = webdriver.ChromeOptions()
    # Remove headless option if you want the browser to be visible.
    # options.add_argument("--headless")
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

def get_all_article_links(driver):
    """Navigate the All Pages index and return a sorted list of article URLs."""
    print("Fetching all article links...")
    article_links = set()

    driver.get(ALL_PAGES_URL)
    time.sleep(2)

    while True:
        current_url = driver.current_url
        print(f"Scraping: {current_url}")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # The links are inside the <div class="mw-allpages-body">
        content_div = soup.find("div", class_="mw-allpages-body")
        if content_div:
            links = content_div.find_all("a")
            for link in links:
                href = link.get("href")
                # Exclude special pages (like Special:...) 
                if href and href.startswith("/wiki/") and not href.startswith("/wiki/Special:"):
                    article_links.add(BASE_URL + href)
        else:
            print("No page content found!")
            break

        # Look for a "Next page" link
        next_link = soup.find("a", string="Next page")
        if next_link:
            next_url = BASE_URL + next_link["href"]
            driver.get(next_url)
            time.sleep(1.5)
        else:
            break

    links_list = sorted(article_links)
    print(f"Found {len(links_list)} article links.")
    return links_list

def extract_article(driver, url):
    """
    Visit the article URL and extract the title, main text, and category names.
    Returns: title (str), text (str), categories (list of str)
    """
    driver.get(url)
    time.sleep(1.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Get the title from element with id "firstHeading"
    title_tag = soup.find(id="firstHeading")
    content_tag = soup.find("div", class_="mw-parser-output")

    if not title_tag or not content_tag:
        print(f"Skipping {url}: missing title or content.")
        return None, None, []

    title = title_tag.get_text(strip=True)
    # Remove unwanted tags (optional: tables, navboxes, references)
    for tag in content_tag.find_all(["table", "div"], class_=lambda x: x and ("navbox" in x or "reference" in x)):
        tag.decompose()

    # Extract text content – join paragraphs and other text blocks.
    text = content_tag.get_text(separator="\n", strip=True)

    # Get categories; these are typically in the div with id "catlinks"
    cat_div = soup.find("div", id="catlinks")
    categories = []
    if cat_div:
        for a in cat_div.find_all("a"):
            # Sometimes the first link is just "Categories"
            cat_text = a.get_text(strip=True)
            if cat_text.lower() != "categories":
                categories.append(cat_text)
    else:
        print(f"No categories found for {title}")
    return title, text, categories

def save_article_in_categories(title, text, categories):
    """
    Save a copy of the article text into folders for each category.
    The first category gets the base filename; subsequent ones add a numeric suffix.
    """
    safe_title = sanitize_filename(title)
    if not categories:
        # Save in an "Uncategorized" folder if no categories were found.
        categories = ["Uncategorized"]

    for idx, category in enumerate(categories):
        cat_folder = os.path.join(DEST_DIR, sanitize_filename(category))
        os.makedirs(cat_folder, exist_ok=True)
        # For the first occurrence, no suffix; then _2, _3, etc.
        suffix = "" if idx == 0 else f"_{idx+1}"
        file_path = os.path.join(cat_folder, f"{safe_title}{suffix}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved '{title}' to '{cat_folder}' as '{os.path.basename(file_path)}'.")

def main():
    driver = get_driver()
    try:
        links = get_all_article_links(driver)
        total = len(links)
        for i, link in enumerate(links, 1):
            print(f"[{i}/{total}] Processing: {link}")
            title, text, categories = extract_article(driver, link)
            if title and text:
                save_article_in_categories(title, text, categories)
            else:
                print(f"Skipping article from {link} due to missing data.")
            # Wait a moment to be polite to the server.
            time.sleep(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
