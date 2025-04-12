import os
import shutil
import time
import requests
from bs4 import BeautifulSoup

SOURCE_DIR = "coppermind_selenium"
DEST_DIR = "coppermind_sorted"
BASE_URL = "https://coppermind.net/wiki/"

def get_categories_from_article(title):
    """Fetch the categories of an article by scraping the wiki page."""
    url = BASE_URL + title.replace(" ", "_")
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        cat_div = soup.find("div", {"id": "catlinks"})
        if not cat_div:
            return []
        categories = [a.text.strip() for a in cat_div.find_all("a") if a.text.strip()]
        return categories
    except Exception as e:
        print(f"Error getting categories for {title}: {e}")
        return []

def sanitize(name):
    return "".join(c for c in name if c.isalnum() or c in " .-_").strip()

def sort_files():
    os.makedirs(DEST_DIR, exist_ok=True)
    all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]

    for i, file in enumerate(all_files):
        filepath = os.path.join(SOURCE_DIR, file)
        title = file.rsplit(".txt", 1)[0]

        print(f"[{i+1}/{len(all_files)}] Sorting: {title}")
        categories = get_categories_from_article(title)

        if not categories:
            print(f"  No categories found. Skipping.")
            continue

        for idx, category in enumerate(categories):
            cat_dir = os.path.join(DEST_DIR, sanitize(category))
            os.makedirs(cat_dir, exist_ok=True)

            suffix = f"_{idx+1}" if idx > 0 else ""
            target_file = os.path.join(cat_dir, sanitize(title) + suffix + ".txt")

            try:
                shutil.copyfile(filepath, target_file)
            except Exception as e:
                print(f"  Failed to copy to {cat_dir}: {e}")

        time.sleep(0.5)  # Be polite to the server

if __name__ == "__main__":
    sort_files()
