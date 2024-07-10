import click

from src.db.utils import upgrade_database
from src.settings import DbSettings


@click.command()
@click.option("--upgrade", is_flag=True, help="Upgrade alembic head")
def cli(upgrade: bool) -> None:
    if upgrade:
        upgrade_database(DbSettings.get_sync_db_url())


if __name__ == "__main__":
    cli()
