import re
import contractions
import string
import bleach
from bs4 import BeautifulSoup

def parse_10k_10q_filing_item7(text):
    # Define regex patterns outside the loop for better performance
    item7_start = re.compile("item\s*[7][\.\;\:\-\_]*\s*\\bM", re.IGNORECASE)
    item7_end = re.compile("item\s*7a[\.\;\:\-\_]\sQuanti|item\s*8[\.\,\;\:\-\_]\s*", re.IGNORECASE)

    # Find all start and end positions using finditer
    starts = [i.start() for i in item7_start.finditer(text)]
    ends = [i.start() for i in item7_end.finditer(text)]

    positions = []
    for s in starts:
        nearest_end = min((e for e in ends if e > s), default=None)
        if nearest_end is not None:
            positions.append([s, nearest_end])

    # Check if positions is not empty before using max
    if positions:
        # Use max() with a key function to find the position with the maximum length
        item_position = max(positions, key=lambda p: p[1] - p[0])
        return text[item_position[0]:item_position[1]]
    else:
        print("Unable to locate Item 7")
        return None

def cleaning(text):
    # $CHALLENGIFY_BEGIN
    # Replace new lines
    text = text.replace('\n', ' ')
    # Removing whitespaces
    text = text.strip()
    # Lowercasing
    text = text.lower()
    # Removing numbers
    text = ''.join(char for char in text if not char.isdigit())
    # Removing contractions
    text = contractions.fix(text)
    # Removing HTML tags
    text = bleach.clean(text, tags=[], strip=True)
    # Removing punctuation
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')

    return text
