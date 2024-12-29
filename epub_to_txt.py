# DEPENDANCY: BeautifulSoup
from ebooklib import epub
from bs4 import BeautifulSoup

def epub_to_txt(epub_path, txt_path):
    book = epub.read_epub(epub_path)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                txt_file.write(soup.get_text())

# Example usage
epub_path = 'path/to/your/file.epub'
txt_path = 'path/to/your/output.txt'
epub_to_txt(epub_path, txt_path)
