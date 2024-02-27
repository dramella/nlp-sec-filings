import io
import glob
import os
import numpy as np
import pandas as pd
import requests
from typing import Union
import unlzw
import secnlp.utils as u


def current_edgar_companies_list(url = "https://www.sec.gov/files/company_tickers.json",
                                agent = "Name Surname name.surname@gmail.com") -> pd.DataFrame:
    """
    Download current list of companies available in the EDGAR database.
    """
    headers = {"User-Agent": agent}
    response = requests.get(url, headers=headers)
    df = pd.DataFrame(data = [d for d in response.json().values()])
    df.rename(columns={'cik_str':'cik','title':'name'},inplace=True)
    df.drop_duplicates(inplace=True,subset=['cik','name'])
    df['cik'] = df['cik'].apply(lambda x: u.add_trailing_zeroes_cik(x))
    df['name'] = df['name'].str.capitalize()
    df.set_index    ('cik',drop=True,inplace=True)
    return df

def basic_info_company(cik: Union[str, int], url: str = "https://data.sec.gov/submissions/CIK",
                       agent: str = "Name Surname name.surname@gmail.com") -> dict:
    """
    Download basic company information for a given CIK.
    """
    cik_str = u.add_trailing_zeroes_cik(str(cik))  # Assuming u.add_trailing_zeroes_cik is defined

    try:
        response = requests.get(f"{url}{cik_str}.json", headers={"User-Agent": agent})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for CIK {cik}: {e}")
        return {}

    data = response.json()
    return data



def bulk_download_url_filings(start_year = 1993, end_year = 2023, quarters = ['QTR1','QTR2','QTR3','QTR4'],
                              agent = "Name Surname name.surname@gmail.com", uncompress = False):
    """
    Download index filex of filings. If uncompress is True, the index files are
    uncompressed and saved as a dataframe.
    """
    headers = {"User-Agent": agent}
    years_list = list(range(start_year, end_year + 1, 1))
    file_type = 'master.Z'
    sub_directory = "./master_data"
    os.makedirs(sub_directory, exist_ok=True)
    for year in years_list:
        for quarter in quarters:
            response = requests.get(f'https://www.sec.gov/Archives/edgar/full-index/{year}/{quarter}/{file_type}',headers=headers)
            file_path = os.path.join(sub_directory, f"{year}_{quarter}_{file_type}")
            with open(file_path, mode="wb") as file:
                file.write(response.content)
    if uncompress is True:
        df_list = []
        for file_path in glob.glob('./master_data/*'):
            with open(file_path, 'rb') as file:
                compressed_data = file.read()
                uncompressed_data = unlzw.unlzw(compressed_data)
                decoded_data = uncompressed_data.decode('latin-1')
                data_io = io.StringIO(decoded_data)
                df = pd.read_csv(data_io, sep='|', header=None, names=['cik','company','form_type','date_filed','file_name'],skiprows=11)
                df_list.append(df)
        df = pd.concat(df_list)
        df['cik'] = df['cik'].apply(lambda x: u.add_trailing_zeroes_cik(x))
        df.set_index('cik', drop = True)
        return df


def scrape_filing(cik: str, accession_number: str, agent: str, base_url: str = 'https://www.sec.gov/Archives/edgar/data') -> str:
    """
    Scrape filings content for a given accession number.
    """
    url = f"{base_url}/{cik}/{accession_number.strip().replace('-','')}/{accession_number.strip()}.txt"

    try:
        response = requests.get(url, headers={"User-Agent": agent})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for accession number {accession_number}: {e}")
        return ""

    return response.text


# Function to fetch content from a URL
def fetch_text_from_url(url, agent):
    full_url = 'https://www.sec.gov/Archives/' + url
    response = requests.get(full_url, headers={"User-Agent": agent})
    if response.status_code == 200:
        return response.text
    else:
        return np.nan
