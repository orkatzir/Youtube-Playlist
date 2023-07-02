from prefect import flow
import os

@flow(name="Run DBT Model")
def trigger_dbt_command():
    os.system("cd C:\\Users\\Or\\Documents\\dbt\\dbt_p && conda activate dbt &&  dbt run")
trigger_dbt_command()