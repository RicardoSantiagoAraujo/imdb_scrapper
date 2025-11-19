import requests
from bs4 import BeautifulSoup
from warnings import warn
from time import sleep
from random import randint
import pandas as pd
import os

# Constants and User-Agent Header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15'
}



def request_and_parse(url, suffix=""):
    """
    Fetches and parses the HTML from the given URL + suffix.

    Args:
        url (str): The base URL of the IMDb page.
        suffix (str): The suffix to append to the base URL (e.g., "fullcredits", "keywords").

    Returns:
        BeautifulSoup: The parsed HTML content of the page.
    """
    response_url = url + suffix
    response = requests.get(response_url, headers=HEADERS)
    # sleep(randint(1, 3))  # Random sleep to avoid throttling
    if response.status_code != 200:
        warn(f'Request: {suffix}; Status code: {response.status_code}')
    return BeautifulSoup(response.text, 'html.parser')

def scrape_metacritic_score(page_html):
    """
    Scrapes the Metacritic score from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the main page.

    Returns:
        str: The Metacritic score, or pd.NA if not found.
    """
    metascore = page_html.find('span', class_='metacritic-score-box')
    return metascore.text if metascore else pd.NA

def scrape_top_cast(page_html):
    """
    Scrapes the top cast members from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the main page.

    Returns:
        list: A list of top cast members, or pd.NA if not found.
    """
    cast = page_html.find_all('a', {'data-testid': 'title-cast-item__actor'})
    return [el.text for el in cast] if cast else pd.NA

def scrape_details(page_html, detail_class):
    """
    Scrapes specific details like country, language, and company from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the main page.
        detail_class (str): The CSS class to search for (e.g., 'title-details-origin' for countries).

    Returns:
        list: A list of details (e.g., countries or languages), or pd.NA if not found.
    """
    detail_block = page_html.find('li', {'data-testid': detail_class})
    if detail_block:
        return [detail.text.strip() for detail in detail_block.find_all('a')]
    return pd.NA

def scrape_profits(page_html, profit_class):
    """
    Scrapes profit-related information (like budget, gross values) from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the main page.
        profit_class (str): The CSS class related to profit data (e.g., 'title-boxoffice-budget').

    Returns:
        list: A list of profit data (budget, gross), or pd.NA if not found.
    """
    profit_block = page_html.find('li', {'data-testid': profit_class})
    if profit_block:
        return [profit.text.strip() for profit in profit_block.find_all('li')]
    return pd.NA

def scrape_credits(page_html, role):
    """
    Scrapes credits for specific roles (e.g., writers, producers, composers) from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the full credits page.
        role (str): The role to scrape (e.g., 'writer', 'producer').

    Returns:
        list: A list of names for the given role, or pd.NA if not found.
    """
    title = page_html.find('h4', {'id': role})
    if title:
        names = title.find_next('table').find_all('a')
        return [name.text.strip().replace("\n", "") for name in names]
    return pd.NA

def scrape_keywords(page_html):
    """
    Scrapes keywords from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the keywords page.

    Returns:
        list: A list of keywords, or pd.NA if not found.
    """
    kws = page_html.find_all('li', {'data-testid': "list-summary-item"})
    return [kw.find('a').text for kw in kws] if kws else pd.NA

def scrape_mpaa_rating(page_html):
    """
    Scrapes the MPAA rating from the parental guide.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the parental guide page.

    Returns:
        str: The MPAA rating, or pd.NA if not found.
    """
    parental = page_html.find('tr', {'id': "mpaa-rating"})
    return parental.find_all("td")[1].text if parental else pd.NA

def scrape_technical_details(page_html, spec_id, html_tag):
    """
    Scrapes technical details like color, aspect ratio, and sound mix from the page HTML.

    Args:
        page_html (BeautifulSoup): The parsed HTML content of the technical page.
        spec_id (str): The specification ID to search for (e.g., 'colorations', 'aspectratio').
        html_tag (str): The HTML tag to search for (e.g., 'a', 'span').

    Returns:
        list: A list of technical details (e.g., colors, aspect ratios), or pd.NA if not found.
    """
    tech = page_html.find("li", {'id': spec_id})
    if tech:
        return [param.text for param in tech.find_all(html_tag)]
    return pd.NA

def scrape_film_data(film_row):
    """
    Scrapes all the film-related data from a given IMDb URL.

    Args:
        film_row (str): The IMDb page URL of the film.

    Returns:
        dict: A dictionary containing all scraped data for the film.
    """
    url = film_row["URL"]
    title = film_row["Title"]
    const = film_row["Const"]

    page_html = request_and_parse(url)
    page_credits_html = request_and_parse(url, "fullcredits")
    page_keywords_html = request_and_parse(url, "keywords")
    page_parental_html = request_and_parse(url, "parentalguide")
    page_technical_html = request_and_parse(url, "technical")

    # Scraping data
    return {
        "Title": title,
        "URL": url,
        "Const": const,
        "Metacritic Score": scrape_metacritic_score(page_html),
        "Top Cast": scrape_top_cast(page_html),
        "Countries": scrape_details(page_html, 'title-details-origin'),
        "Languages": scrape_details(page_html, 'title-details-languages'),
        "Companies": scrape_details(page_html, 'title-details-companies'),
        "Budget": scrape_profits(page_html, 'title-boxoffice-budget'),
        "Gross Domestic": scrape_profits(page_html, 'title-boxoffice-grossdomestic'),
        "Gross Domestic Opening WE": scrape_profits(page_html, 'title-boxoffice-openingweekenddomestic'),
        "Gross Worldwide": scrape_profits(page_html, 'title-boxoffice-cumulativeworldwidegross'),
        "Writers": scrape_credits(page_credits_html, "writer"),
        "Producers": scrape_credits(page_credits_html, "producer"),
        "Composers": scrape_credits(page_credits_html, "composer"),
        "Cinematographers": scrape_credits(page_credits_html, "cinematographer"),
        "Editors": scrape_credits(page_credits_html, "editor"),
        "Keywords": scrape_keywords(page_keywords_html),
        "MPAA Rating": scrape_mpaa_rating(page_parental_html),
        "Colors": scrape_technical_details(page_technical_html, "colorations", "a"),
        "Aspect Ratios": scrape_technical_details(page_technical_html, "aspectratio", "span"),
        "Sound Mixes": scrape_technical_details(page_technical_html, "soundmixes", "a")
    }



def get_existing_rows(file_path):
    """
    Reads the CSV file at the given path and returns the data in the specified columns.
    If the file doesn't exist or is empty, returns an empty DataFrame with columns ["Const", "Title", "URL"].

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The DataFrame with columns ["Const", "Title", "URL"], or an empty DataFrame if file is empty or doesn't exist.
    """
    try:
        # Attempt to read the CSV file
        existing_rows = pd.read_csv(file_path)[["Const", "Title", "URL"]]

        # If the DataFrame is empty, create an empty DataFrame
        if existing_rows.empty:
            print(f"The file {file_path} is empty. Returning an empty DataFrame.")
            existing_rows = pd.DataFrame(columns=["Const", "Title", "URL"])

    except (FileNotFoundError, pd.errors.EmptyDataError):
        # If the file doesn't exist or is empty, return an empty DataFrame
        print(f"The file {file_path} does not exist or is empty. Returning an empty DataFrame.")
        existing_rows = pd.DataFrame(columns=["Const", "Title", "URL"])

    return existing_rows


def append_or_create_csv(scraped_data, file_path):
    """
    Appends new scraped data to an existing CSV file, or creates the file if it doesn't exist.

    Args:
        scraped_data (list or DataFrame): The new data to be appended or saved.
        file_path (str): The path to the CSV file where the data should be saved or appended.

    Returns:
        pd.DataFrame: The DataFrame after appending new data or creating a new file.
    """
    if os.path.exists(file_path):
        # If the file exists, read the existing data
        existing_data = pd.read_csv(file_path)
        # Convert the scraped data to DataFrame if it is a list or another format
        new_data = pd.DataFrame(scraped_data)
        # Concatenate the old and new DataFrames
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv(file_path, index=False)  # Save back to the same file
        print(f"Appended new data to {file_path}.")
    else:
        # If the file doesn't exist, create a new one
        new_data = pd.DataFrame(scraped_data)
        new_data.to_csv(file_path, index=False)
        print(f"Created new file {file_path} with the data.")
        combined_data = new_data

    return combined_data

def merge_and_save(merged_df, input_path, output_path):
    """
    Merges the scraped data with the input ratings file and saves the result.

    Args:
        merged_df (pd.DataFrame): The DataFrame to be merged with the ratings.
        input_path (str): Path to the input ratings CSV.
        output_path (str): Path to save the merged DataFrame.
    """
    my_ratings = pd.read_csv(input_path)

    # Merge the DataFrames (using 'left' to keep all rows from ratings)
    extended_films = pd.merge(my_ratings, merged_df, how='left', on=["Const","Title", "URL"])

    # Save the merged DataFrame to the output file
    extended_films.to_csv(output_path, index=False)
    print(f"Merged data saved to {output_path}.")
