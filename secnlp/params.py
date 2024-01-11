import os

##################  VARIABLES  ##################
AGENT = os.environ.get("AGENT")
PROJECT = os.environ.get("GCP_PROJECT_ID")
DATASET_ID = os.environ.get("BQ_DATASET")
SERVICE_ACCOUNT = os.environ.get("SERVICE_ACCOUNT")
FILINGS_10KQ_TABLE_ID = os.environ.get("FILINGS_10KQ_TABLE_ID")
