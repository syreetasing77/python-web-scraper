
"""
Books to Scrape - Python Jumpstart Mentorship Project
======================================================

A beginner-friendly web scraper that extracts book data from
http://books.toscrape.com -- a sandbox site built specifically for
practicing web scraping (no terms of service to worry about).

This scraper demonstrates these beginner Python concepts:
  - imports & third-party libraries
  - functions (def)
  - lists and dictionaries
  - for loops and conditionals (if statements)
  - string slicing
  - file I/O (writing a CSV)
  - basic error handling

Run it from the command line:
    python scraper.py

Output:
    A file called books_data.csv in the same folder.
"""

# ---------- IMPORTS ----------
# These are the libraries our program needs.
# requests:        downloads web pages over HTTP
# BeautifulSoup:   parses HTML so we can pull out the parts we want
# csv:             a built-in library for writing CSV files
# time:            a built-in library; we use it to pause between requests

import requests                       # third-party (pip install requests)
from bs4 import BeautifulSoup         # third-party (pip install beautifulsoup4)
import csv                            # built-in -- comes with Python
import time                           # built-in


# ---------- CONFIG ----------
# Putting settings at the top makes the program easy to tweak later.
BASE_URL = 'http://books.toscrape.com/catalogue/page-{}.html'   # the {} is a placeholder
PAGES_TO_SCRAPE = 5            # how many pages of books to grab (50 pages exist)
OUTPUT_FILE = 'books_data.csv'
PAUSE_SECONDS = 1              # how long to wait between page requests (be polite)

# This is a DICTIONARY -- it maps text labels to numbers.
# We'll use it to convert "Three" -> 3 later in the code.
RATING_MAP = {
    'One':   1,
    'Two':   2,
    'Three': 3,
    'Four':  4,
    'Five':  5,
}


# ---------- FUNCTIONS ----------
# A function is a reusable block of code. We define each one with `def`.

def get_page(url):
    """Download a page and return a BeautifulSoup object we can search.

    A function takes inputs (here: a url) and returns an output
    (here: parsed HTML).
    """
    response = requests.get(url)                            # ask the server for the page
    response.raise_for_status()                             # crash loudly if something went wrong
    soup = BeautifulSoup(response.text, 'html.parser')      # parse the HTML
    return soup


def parse_rating(book_card):
    """Pull the star rating out of a book card and turn it into a number (1-5).

    The site shows ratings as a CSS class like 'star-rating Three'.
    We grab that class list, take the second word, and look it up in our
    RATING_MAP dictionary.
    """
    rating_tag = book_card.find('p', class_='star-rating')

    # rating_tag['class'] is a LIST like ['star-rating', 'Three']
    rating_word = rating_tag['class'][1]    # SLICING -- grab the item at index 1

    # .get() returns 0 if the word isn't found in the dictionary (safe lookup)
    return RATING_MAP.get(rating_word, 0) 


def extract_book(book_card):
    """Take one book card (HTML element) and return a dictionary of its data.

    Dictionaries are key/value pairs -- like a tiny labeled record.
    """
    # Title is stored in the link's `title` attribute, not its text
    title = book_card.h3.a['title']

    # Price text looks like '£51.77' -- we slice off the '£' and convert to a float
    price_text = book_card.find('p', class_='price_color').text
    price = float(price_text.encode('ascii', 'ignore').decode().strip())         # SLICING again -- skip the first character

    rating = parse_rating(book_card)        # call our helper function

    # .strip() removes leading/trailing whitespace
    availability = book_card.find('p', class_='instock availability').text.strip()

    # Build the full URL by combining the base with the relative link
    relative_url = book_card.h3.a['href']
    full_url = 'http://books.toscrape.com/catalogue/' + relative_url.replace('../../../', '')

    # Return a DICTIONARY -- this represents one row of our final CSV.
    return {
        'title':        title,
        'price_gbp':    price,
        'rating':       rating,
        'availability': availability,
        'url':          full_url,
    }


def scrape_page(page_number):
    """Scrape every book on a single page and return them as a list."""
    url = BASE_URL.format(page_number)      # fill in the {} placeholder
    print(f'  Scraping page {page_number}: {url}')

    soup = get_page(url)
    book_cards = soup.find_all('article', class_='product_pod')   # one card per book

    books = []                              # this is a LIST -- it'll grow as we add books
    for card in book_cards:                 # this is a FOR LOOP -- one trip per book
        book = extract_book(card)
        books.append(book)                  # add the dictionary to our list

    return books


def save_to_csv(books, filename):
    """Write the list of book dictionaries to a CSV file."""
    if not books:                           # CONDITIONAL -- if the list is empty, bail out
        print('No books to save!')
        return


    # csv.DictWriter knows how to turn dictionaries into CSV rows.
    fieldnames = list(books[0].keys())      # use the first dict's keys as headers

    # `with open(...)` automatically closes the file when we're done -- safer than open/close
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()                # write the column names
        writer.writerows(books)             # write every dictionary in the list

    print(f'\nSaved {len(books)} books to {filename}')


def print_summary(books):
    """Print a quick summary so the user sees results in the terminal."""
    if not books:
        return

    total = len(books)
    avg_price = sum(b['price_gbp'] for b in books) / total

    # This is a LIST COMPREHENSION -- a compact way to build a new list.
    # It says: "give me every book whose rating is 5".
    five_stars = [b for b in books if b['rating'] == 5]

    print('\n----- SUMMARY -----')
    print(f'Total books scraped:  {total}')
    print(f'Average price:        £{avg_price:.2f}')
    print(f'5-star books:         {len(five_stars)}')

    if five_stars:
        print('Sample 5-star titles:')
        for book in five_stars[:3]:         # SLICING -- first 3 items only
            print(f'  - {book["title"]}')


# ---------- MAIN ----------
def main():
    """The entry point -- where the program actually starts running."""
    print(f'Starting scrape of {PAGES_TO_SCRAPE} pages...\n')

    all_books = []
    for page_num in range(1, PAGES_TO_SCRAPE + 1):    # range(1, 6) -> 1, 2, 3, 4, 5
        page_books = scrape_page(page_num)
        all_books.extend(page_books)        # extend() adds every item from another list
        time.sleep(PAUSE_SECONDS)           # pause between requests -- don't hammer the site

    save_to_csv(all_books, OUTPUT_FILE)
    print_summary(all_books)


# This little block makes sure main() only runs when you run THIS file directly.
# It won't run if some other script imports this file.
if __name__ == '__main__':
    main()
