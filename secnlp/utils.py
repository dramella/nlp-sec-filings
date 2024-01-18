
import pandas as pd
from google.cloud import bigquery

def add_trailing_zeroes_cik(x):
    if len(str(x)) < 10:
        return (10 - len(str(x))) * str(0) + str(x)
    else:
        return str(x)

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

    client = bigquery.Client.from_service_account_json(credentials)

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
