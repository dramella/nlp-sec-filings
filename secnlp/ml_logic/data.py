import os
import io
import glob
import unlzw
import requests
import pandas as pd
from google.cloud import bigquery
from secnlp.utils import add_trailing_zeroes_cik


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
    df['cik'] = df['cik'].apply(lambda x: add_trailing_zeroes_cik(x))
    df['name'] = df['name'].str.capitalize()
    df.set_index('cik',drop=True,inplace=True)
    return df

def basic_info_company(cik_list: list,url = "https://data.sec.gov/submissions/",
                       agent = "Name Surname name.surname@gmail.com") -> pd.DataFrame:
    """
    Dowbload basic company information for a list of CIKs.
    """
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
    df['cik'] = df['cik'].apply(lambda x: add_trailing_zeroes_cik(x))
    df.set_index('cik',drop=True,inplace=True)
    return df

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
        df['cik'] = df['cik'].apply(lambda x: add_trailing_zeroes_cik(x))
        df.set_index('cik', drop = True)
        return df

def scrape_filings(fnames, agent, base_url = 'https://www.sec.gov/Archives/'):
    filings = []

    with requests.Session() as session:
        for index, f in enumerate(fnames):
            full_url = base_url + f
            try:
                response = session.get(full_url, headers={"User-Agent": agent})
                response.raise_for_status()  # Raises an HTTPError for bad responses
                filings.append(response.text)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {full_url}: {e}")
                filings.append('NA')

    return filings

def load_data_to_bq(
        credentials: str,
        data: pd.DataFrame,
        gcp_project:str,
        bq_dataset:str,
        table: str,
        truncate: bool):
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand if `truncate` is True, append otherwise
    """

    assert isinstance(data, pd.DataFrame)
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"

    data.columns = [f"_{column}" if not str(column)[0].isalpha() and not str(column)[0] == "_" else str(column) for column in data.columns]

    client = bigquery.Client(credentials)

    # Define write mode and schema
    write_mode = "WRITE_TRUNCATE" if truncate else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    print(f"\n{'Write' if truncate else 'Append'} {full_table_name} ({data.shape[0]} rows)")

    # Load data
    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    result = job.result()  # wait for the job to complete

    print(f"✅ Data saved to bigquery, with shape {data.shape}")

def read_data_from_bq(
        credentials: str,
        gcp_project:str,
        bq_dataset:str,
        table: str):
    """
    - Read BigQuery table as a DataFrame
    """
    client = bigquery.Client.from_service_account_json(credentials)
    # Fetch the data from BigQuery into a DataFrame
    query_job = client.query(f"SELECT * FROM {gcp_project}.{bq_dataset}.{table}")
    return query_job.to_dataframe()
