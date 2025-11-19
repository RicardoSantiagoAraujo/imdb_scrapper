import pandas as pd
from datetime import datetime
from time import sleep
from random import randint
import utils as utils
from rich import print


def main():
    """
    Main function to run the scraper on a list of movies and save the results to CSV.

    Reads the input CSV with IMDb URLs, scrapes data for each film, and saves the results to a CSV file.
    It also merges the scraped data with the original ratings data and saves the extended dataset.
    """
    start_time = datetime.now()
    print(f'[blue]***** IMDB Scraper *****[/blue]\n')
    print(f"Start time: {start_time}")

    # Read input CSV with movie URLs
    pages = pd.read_csv("./inputs/ratings.csv")[["Const", "Title", "URL"]]

    # Get already scraped entries
    existing_rows = utils.get_existing_rows("./outputs/scraped_data.csv")

    # Initialize empty list to store results
    scraped_data = []

    # How many rows to scrap
    startAt=1759
    stopAt= len(pages)
    # stopAt= 6

    for count, row in pages.iloc[startAt:stopAt].iterrows():
        print(f"Processing {count + 1}/{stopAt}: {row['Title']} ({row['Const']}) : {row['URL']}")
        if row["Const"] in existing_rows["Const"].values:
            print("\t [yellow]Entry already scraped. Skipping row.[/yellow]\n")
            continue
        film_data = utils.scrape_film_data(row)
        scraped_data.append(film_data)
        print("\t [green]Entry added.[/green]\n")

    if len(scraped_data)== 0:
        print("\n[yellow] No new entries added. Terminating.[/yellow]")
        return
    # File paths
    scraped_data_file = './outputs/scraped_data.csv'
    ratings_file = './inputs/ratings.csv'
    extended_ratings_file = './outputs/ratings_extended.csv'

    # Step 1: Append or create scraped_data.csv
    merged_scraped_data = utils.append_or_create_csv(scraped_data, scraped_data_file)

    # Step 2: Merge the new data with the ratings file and save
    utils.merge_and_save(merged_scraped_data, ratings_file, extended_ratings_file)

    end_time = datetime.now()
    print("====================")
    print("\t [green]FINISHED[/green]")
    print(f"End time: {end_time}")
    print(f"Duration: {end_time - start_time}")
    print(f"Total new rows: {len(scraped_data)}")


if __name__ == "__main__":
    main()