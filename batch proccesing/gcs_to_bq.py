from pathlib import Path
import pandas as pd
from prefect import flow,task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(name="Get GCS Data")
def extract_from_gcs(playlist_name:str) -> Path:
    """Download trip data from GCS"""

    gcs_path = f"data/DTC_{playlist_name}_playlist_snapshot.parquet"
    gcs_block = GcsBucket.load("gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"./data/")
    local_path="./data/DTC_"+playlist_name+"_playlist_snapshot.parquet"
    print(local_path)
    return Path(local_path)
@task(name="Read Dataframe")
def read_date(path:Path) -> pd.DataFrame:
    df=pd.read_parquet(path) 
    print(f"number of rows: {len(df)}")
    return df

@task(name="Write Dataframe To BigQuery")
def write_bq(df: pd.DataFrame,playlist_name:str) -> None:
    """Write DataFrame to BigQuery"""
    gcp_credentials_block = GcpCredentials.load("gcp")
    playlist_name=playlist_name.replace("!","")
    df.to_gbq(destination_table=f"youtube_playlist.youtube_playlist_{playlist_name}_info",
        project_id="feisty-oxide-385407",
        credentials= gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists="replace"
    )
    return

@flow(name="ETL-TO-BIG-QUERY")
def etl_gcs_to_bq(playlist_name:str) -> None:
    """Main ETL flow to load data into Big Query"""
    
    path = extract_from_gcs(playlist_name)
    df = read_date(path)
    write_bq(df,playlist_name)
    
@flow(name="Parent to ETL-TO-BIG-QUERY")
def parent_etl_gcs_to_bq(playlist_name_list:list[str]) -> None:
    for playlist in playlist_name_list:
        etl_gcs_to_bq(playlist)
        

if __name__ == '__main__':
    playlist_name_list = ['Inside Look At Tech!']
    parent_etl_gcs_to_bq(playlist_name_list)