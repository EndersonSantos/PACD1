import click
import pandas as pd

from atp.cleaning import clean_df

@click.group()
def cli():
    # At the moment all options belong to train command so this is empty
    pass


@click.command()
@click.option(
    "--country",
    help="The country that we going to perform the training",
    default="Switzerland"
)
def train(country):
    df = pd.read_json('atpplayers.json', lines=True)
    df_f = clean_df(df, country)
    df_f.to_csv(f"df_f_{country}.csv")



cli.add_command(train)

if __name__ == "__main__":
    cli()