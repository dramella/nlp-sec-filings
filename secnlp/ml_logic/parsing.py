import re
import contractions
import string
import bleach
from bs4 import BeautifulSoup



def parse_10k_filing_items(text,item = '7'):
    text = clean_text(text)
    # Define regex patterns outside the loop for better performance
    if item == '7':
        #item_start = re.compile("item\s*[7][\.\;\:\-\_]*\s*\\bM", re.IGNORECASE)
        item_start = re.compile(r"item\s*7\s*.*?ma",re.IGNORECASE)
        item_end = re.compile("item\s*7a\s*Quanti|item\s*8", re.IGNORECASE)
    if item == '7a':
        item_start = re.compile(r"Item\s*7A[\s\S]*?\bQu", re.IGNORECASE)
        item_end = re.compile(r"Item\s*8[\s\S]*?\bFI", re.IGNORECASE)
    elif item == '1':
        item_start = re.compile("item\s*1*\s*(Business|Description)", re.IGNORECASE)
        item_end = re.compile("item\s*1[abc]\s*(?:Risk|Unresolved|Cyber)|item\s*2\s*Properties", re.IGNORECASE)
    elif item == '1a':
        item_start = re.compile("item\s*1[a]*\s*R", re.IGNORECASE)
        item_end = re.compile("item\s*1[bc]\s*(?:Unresolved|Cyber)|item\s*2\s*Properties", re.IGNORECASE)

    # Find all start and end positions using finditer
    starts = [i.start() for i in item_start.finditer(text)]
    ends = [i.start() for i in item_end.finditer(text)]

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
        print(f"Unable to locate Item {item}")
        return None


def parse_10q_filing_items(text,item = '2'):
    text = clean_text(text)
    # Define regex patterns outside the loop for better performance
    if item == '2':
        item_start = re.compile(r"Item\s*2[\s\S]*?\bMa", re.IGNORECASE)
        item_end = re.compile(r"Item\s*3[\s\S]*?\bQu", re.IGNORECASE)
    if item == '1a':
        item_start = re.compile(r"Item\s*1A\.[\s\S]*?(?=\bRi)", re.IGNORECASE)
        item_end = re.compile(r"Item\s*5\.[\s\S]*?(?=\bOt)", re.IGNORECASE)

    # Find all start and end positions using finditer
    starts = [i.start() for i in item_start.finditer(text)]
    ends = [i.start() for i in item_end.finditer(text)]

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
        print(f"Unable to locate Item {item}")
        return None

def clean_text(text):
    # Combine replacements
    replacements = {
        '&#160;': ' ',
        '&#xa0;': ' ',
        '&nbsp;': ' ',
        '-': ' ',
        '&amp;': '&',
        '&#38;': '&',
        '\n': ' ',
        '&#8211;': '',  # En dash
        '&#8212;': '',  # Em dash
        '&#8220;': '',  # Left double quotation mark
        '&#8221;': '',  # Right double quotation mark
        '&#8216;': '',  # Left single quotation mark
        '&#8217;': '',  # Right single quotation mark
        '&#8230;': '',  # Ellipsis
        # Add more Unicode codes as needed
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove HTML tags and their content
    text = re.sub(r'<[^>]*>', ' ', text)

    # Remove URLs
    text = re.compile(r'https?://\S+|www\.\S+').sub('', text)

    # Convert to lowercase
    text = text.lower()

    # Removing contractions
    text = contractions.fix(text)

    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)

    # Remove irrelevant characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    return text
