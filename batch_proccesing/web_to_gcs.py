from pathlib import Path
import pandas as pd
from youtube_watcher import main as youtube_watcher

from prefect import flow,task
from prefect_gcp.cloud_storage import GcsBucket

@task(name="Fetch Data")
def fetch(playlist_id:str) -> pd.DataFrame:

    #run youtube_watcher and get the dataframe
    df,playlist_name = youtube_watcher(playlist_id)
    
    return df,playlist_name

@task(name="Clean Data")
def clean_and_edit(df: pd.DataFrame,playlist_name:str) -> pd.DataFrame:
    df['publishedAt']  = pd.to_datetime(df['publishedAt'])
    df['channelTitle'] = df['channelTitle'].astype(str)
    df['playlist_name'] = playlist_name

    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"number of rows: {len(df)}")
    print(playlist_name)
    return df

@task(name="Save Parquet Locally")
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    path = Path(f"data/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task(name="Save Parquet GCS")
def write_gcs(path: Path) -> None:

    gcp_cloud_storage_bucket_block = GcsBucket.load("gcs")
    gcp_cloud_storage_bucket_block.upload_from_path(
        from_path=f"{path}",
        to_path=(path._str).replace("\\","/")
    )
    return

@flow(name="etl web to gcs")
def etl_web_to_gcs(playlist_id:str) -> None:

    df,playlist_name = fetch(playlist_id)
    df_clean = clean_and_edit(df,playlist_name)
    dataset_file = f'DTC_{playlist_name}_playlist_snapshot'
    path = write_local(df_clean,dataset_file)
    write_gcs(path)

@flow(name="parent_flow web to gcs")
def etl_parent_web_to_gcs(playlist_id_list:list[str]) -> None:

    for playlist_id in playlist_id_list:
        etl_web_to_gcs(playlist_id)

if __name__ == '__main__':
    playlist_id_list = ["PLJYIzyhJUEpjw6p-8iJS_iDlCbbeE_qb2"]
    etl_parent_web_to_gcs(playlist_id_list)