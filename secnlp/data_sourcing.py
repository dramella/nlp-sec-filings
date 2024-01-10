import os
import io
import glob
import requests
from unlzw import unlzw
import pandas as pd

def current_edgar_companies_list(url = "https://www.sec.gov/files/company_tickers.json",
                                 agent = "Name Surname name.surname@gmail.com"):
    headers = {"User-Agent": agent}
    response = requests.get(url, headers=headers)
    df = pd.DataFrame(data = [d for d in response.json().values()])
    df.rename(columns={'cik_str':'cik','title':'name'},inplace=True)
    df.drop_duplicates(inplace=True,subset=['cik','name'])
    df['cik'] = df['cik'].map(lambda x: (10-len(str(x)))*str(0) + str(x) if len(str(x))<10 else str(x))
    df['name'] = df['name'].str.capitalize()
    df.set_index('cik',drop=True,inplace=True)
    return df

def basic_info_company(cik_list,url = "https://data.sec.gov/submissions/",
                       agent = "Name Surname name.surname@gmail.com"):
    headers = {"User-Agent": agent}
    sliced_keys=['cik','sic','sicDescription','tickers','exchanges','fiscalYearEnd']
    company_basic_info_df_list = []
    for i in cik_list:
        company_facts_url = url + f'CIK{i}.json'
        response = requests.get(company_facts_url, headers=headers)
        sliced_dict = {key: response.json()[key] for key in sliced_keys}
        company_basic_info_df_list.append(pd.DataFrame(sliced_dict))
    df = pd.concat(company_basic_info_df_list)
    df.drop_duplicates('cik', inplace=True)
    df.set_index('cik',drop=True,inplace=True)
    return df

def bulk_download_url_filings(start_year = 1993, end_year = 2023, quarters = ['QTR1','QTR2','QTR3','QTR4'],
                              agent = "Name Surname name.surname@gmail.com", uncompress = False):
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
                uncompressed_data = unlzw(compressed_data)
                decoded_data = uncompressed_data.decode('latin-1')
                data_io = io.StringIO(decoded_data)
                df = pd.read_csv(data_io, sep='|', header=None, names=['cik','company','form_type','date_filed','file_name'],skiprows=11)
                df_list.append(df)
        df = pd.concat(df_list)
        df['cik'] = df['cik'].map(lambda x: (10-len(str(x)))*str(0) + str(x) if len(str(x))<10 else str(x))
        df.set_index('cik', drop = True)
        return df

def download_raw_filing(fname, base_url = 'https://www.sec.gov/Archives/', agent = "Name Surname name.surname@gmail.com"):
    full_url = base_url + fname
    response = requests.get(full_url, headers = {"User-Agent":"Debora Ramella debora.ramell@gmail.com"})
    if response.status_code != 200:
        return f"Unable to download from {full_url}"
    return response.text
