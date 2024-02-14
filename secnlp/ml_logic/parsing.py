import re
import contractions
import string
import bleach
from bs4 import BeautifulSoup


def parse_10k_filing_items(text,item = '7'):
    # Define regex patterns outside the loop for better performance
    if item == '7':
        #item_start = re.compile("item\s*[7][\.\;\:\-\_]*\s*\\bM", re.IGNORECASE)
        item_start = re.compile(r"item\s*7[^\w]*\s*(?:&\w+;|\d+\.)*\s*(?:</?b>)?\s*m",re.IGNORECASE)
        item_end = re.compile("item\s*7a[\.\;\:\-\_]\sQuanti|item\s*8[\.\,\;\:\-\_]\s*", re.IGNORECASE)
    if item == '7a':
        item_start = re.compile(r"Item\s*7A[\s\S]*?\bQu", re.IGNORECASE)
        item_end = re.compile(r"Item\s*8[\s\S]*?\bFI", re.IGNORECASE)
    elif item == '1':
        item_start = re.compile("item\s*1[\.\;\:\-\_]*\s*Business", re.IGNORECASE)
        item_end = re.compile("item\s*1[abc][\.\,\;\:\-\_]\s*(?:Risk|Unresolved|Cyber)|item\s*2[\.\,\;\:\-\_]\s*Properties", re.IGNORECASE)
    elif item == '1a':
        item_start = re.compile("item\s*1[a][\.\;\:\-\_]*\s*R", re.IGNORECASE)
        item_end = re.compile("item\s*1[bc][\.\,\;\:\-\_]\s*(?:Unresolved|Cyber)|item\s*2[\.\,\;\:\-\_]\s*Properties", re.IGNORECASE)

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


def parse_10q_filing_items(text,item = '7'):
    # Define regex patterns outside the loop for better performance
    if item == '2':
        item_start = re.compile(r"Item\s*2[\s\S]*?\bMa", re.IGNORECASE)
        item_end = re.compile(r"Item\s*3[\s\S]*?\bQu", re.IGNORECASE)
    if item == '1a':
        item_start = re.compile(r"Item\s*1A\.[\s\S]*?(?=\bRisk Factors\b)", re.IGNORECASE)
        item_end = re.compile(r"Item\s*5\.[\s\S]*?(?=\bOther Information\b)", re.IGNORECASE)

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

def cleaning(text):
    # Removing HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    for table in soup.find_all('table'):
        table.decompose()
    text = soup.get_text(separator=' ', strip=True)
    # Replace new lines
    text = text.replace('\n', ' ')
    # Removing URLs
    text = re.compile(r'https?://\S+|www\.\S+').sub('', text)
    # Lowercasing
    text = text.lower()
    # Removing contractions
    text = contractions.fix(text)
    # Removing punctuation
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
        # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
        # Removing irrelevant characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    return text
