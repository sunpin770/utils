import os
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://coppermind.net"
ALL_PAGES_URL = f"{BASE_URL}/wiki/Special:AllPages"
# Use your custom destination folder:
SAVE_ROOT = "C:\\Users\\Srulik's User\\Downloads\\ytdlp downloads\\The Coppermind"

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)

def already_saved(title):
    base = sanitize_filename(title)
    for root, dirs, files in os.walk(SAVE_ROOT):
        for file in files:
            if file.startswith(base):
                return True
    return False

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    # Uncomment the next line if you want headless mode
    # options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_all_article_links(driver):
    print("Fetching all article links...")
    links = set()
    driver.get(ALL_PAGES_URL)

    while True:
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_links = soup.select("#mw-content-text ul li a")
        for a in page_links:
            href = a.get("href")
            if href and href.startswith("/wiki/") and not href.startswith("/wiki/Special:"):
                full_url = BASE_URL + href
                links.add(full_url)
        # Use visible text to pick out the next page link.
        next_link = soup.find("a", text=lambda t: t and t.strip().startswith("Next page"))
        if next_link and next_link.get("href"):
            next_url = BASE_URL + next_link.get("href")
            print(f"Following: {next_url}")
            driver.get(next_url)
        else:
            break

    return sorted(links)

def download_article_selenium(driver, url):
    """Load an article page using Selenium and extract title, content, and categories."""
    driver.get(url)
    time.sleep(2)  # Wait for the page to load
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title_tag = soup.find("h1", id="firstHeading")
    content_tag = soup.find("div", class_="mw-parser-output")
    category_links = soup.select("#mw-normal-catlinks ul li a")

    if not title_tag or not content_tag:
        print(f"Skipping malformed page: {url}")
        return None, None, None

    title = title_tag.text.strip()
    content = content_tag.get_text(separator="\n").strip()
    categories = [cat.text.strip() for cat in category_links]
    return title, content, categories

def save_article(title, content, categories):
    base_filename = sanitize_filename(title) + ".txt"
    if not categories:
        categories = ["Uncategorized"]

    for i, cat in enumerate(categories):
        folder = os.path.join(SAVE_ROOT, sanitize_filename(cat))
        os.makedirs(folder, exist_ok=True)

        # For the first copy we don't add a suffix; subsequent copies get a numeric suffix.
        suffix = f"_{i}" if i > 0 else ""
        filename = sanitize_filename(title) + suffix + ".txt"
        path = os.path.join(folder, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved '{title}' to '{folder}' as '{filename}'.")

def main():
    driver = get_driver()
    try:
        article_links = get_all_article_links(driver)
        print(f"Found {len(article_links)} articles.")
        for idx, url in enumerate(article_links):
            # Generate a guess for the title from the URL (for skipping purposes)
            title_guess = url.rsplit("/", 1)[-1].replace("_", " ")
            if already_saved(title_guess):
                print(f"[{idx+1}/{len(article_links)}] Skipping (already saved): {title_guess}")
                continue

            print(f"[{idx+1}/{len(article_links)}] Processing: {url}")
            title, content, categories = download_article_selenium(driver, url)
            if title and content:
                save_article(title, content, categories)
            else:
                print(f"Skipping article due to missing data: {url}")
            time.sleep(1)  # Be polite
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
