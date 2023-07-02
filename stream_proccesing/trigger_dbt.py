from prefect import flow
from prefect_dbt.cli.commands import trigger_dbt_cli_command

@flow
def trigger_dbt() -> str:
    result = trigger_dbt_cli_command("dbt run   --project-dir C:\\Users\\Or\\Documents\\dbt\\dbt_p\\dbt_project.yml --profiles-dir C:\\Users\\Or\\.dbt\\profiles.yml")
    return result # Returns last line of CLI output

trigger_dbt()