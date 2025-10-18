# IMDB scraper
# Used to flexibly obtain additional data on films from an input list

from requests import get
from bs4 import BeautifulSoup
from warnings import warn
from time import sleep
from random import randint
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime

# Note this takes about 40 min to run if np.arange is set to 9951 as the stopping point.

### my own list of films:
pages = pd.read_csv("./ratings.csv")[["Const", "Title", "URL"]]
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15'
}

# Initialize empty lists to store the variables scraped
const = []
title = []
url = []

# New vars:
metacritic_scores = []
top_casts = []
writers = []
producers = []
composers = []
cinematographers = []
editors = []
countries = []
languages = []
companies = []
budgets = []
grosses_domestic = []
grosses_domestic_opening_we = []
grosses_ww = []
keywords = []
mpaa_ratings = []
colors = []
aspect_ratios = []
sound_mixes = []

# Data scraper
start_time = datetime.now()
print(start_time)

desired_range = range(0, 2)

for count, page in enumerate(pages["URL"][desired_range]):
    elapsed_time = datetime.now() - start_time
    print(elapsed_time)

    print("======================================")
    print(f'\n\t Page {count + 1} out of {len(desired_range)}.')
    perc_completed = count / len(desired_range) * 100
    print(f'\t {perc_completed}% of pages have been scraped.')
    if count > 0:
        print(f'\t Estimated time left till completion: {elapsed_time * 100 / (perc_completed + 0.001) - elapsed_time}.')
    print("\n\t *** " + pages["Title"][count] + " ***")
    print("\t" + pages["URL"][count] + "\n")

    const.append(pages["Const"][count])
    title.append(pages["Title"][count])
    url.append(pages["URL"][count])

    def request_and_parse(txt=""):
        response_url = page + txt
        response = get(response_url, headers=headers)
        sleep(randint(2, 7))
        if response.status_code != 200:
            warn('Request: {}; Status code: {}\n'.format(txt, response.status_code))
        html = BeautifulSoup(response.text, 'html.parser')
        return html

    page_main_html = request_and_parse()
    page_credits_html = request_and_parse("fullcredits")
    page_keywords_html = request_and_parse("keywords")
    page_parental_html = request_and_parse("parentalguide")
    page_technical_html = request_and_parse("technical")

    # Main page: metacritic score
    metascore = page_main_html.find('span', class_='metacritic-score-box')
    if metascore:
        metacritic_scores.append(metascore.text)
    else:
        print("Empty value.")
        metacritic_scores.append(pd.NA)

    # Top cast members
    cast = page_main_html.find_all('a', {'data-testid': 'title-cast-item__actor'})
    if cast:
        top_casts.append([el.text for el in cast])
    else:
        print("Empty value.")
        top_casts.append(pd.NA)

    def detail_scraper(target_list, detail):
        detail_block = page_main_html.find('li', {'data-testid': detail})
        if detail_block:
            details = detail_block.find_all('a')
            target_list.append([det.text.strip() for det in details])
        else:
            print("Empty value.")
            target_list.append(pd.NA)

    detail_scraper(countries, 'title-details-origin')
    detail_scraper(languages, 'title-details-languages')
    detail_scraper(companies, 'title-details-companies')

    # Clean company data
    for el in companies[count]:
        if len(el) == 0:
            companies[count].remove(el)
    if companies[count] and "Production" in companies[count][0]:
        del companies[count][0]

    def profit_scraper(target_list, measurement):
        measurement_block = page_main_html.find('li', {'data-testid': measurement})
        if measurement_block:
            measurements = measurement_block.find_all('li')
            target_list.append([mes.text.strip() for mes in measurements])
        else:
            print("Empty value.")
            target_list.append(pd.NA)

    profit_scraper(budgets, 'title-boxoffice-budget')
    profit_scraper(grosses_domestic, 'title-boxoffice-grossdomestic')
    profit_scraper(grosses_domestic_opening_we, 'title-boxoffice-openingweekenddomestic')
    profit_scraper(grosses_ww, 'title-boxoffice-cumulativeworldwidegross')

    def credits_scraper(target_list, role):
        title = page_credits_html.find('h4', {'id': role})
        if title:
            names = title.find_next('table').find_all('a')
            target_list.append([name.text.strip().replace("\n", "") for name in names])
        else:
            print("Empty value.")
            target_list.append(pd.NA)

    credits_scraper(writers, "writer")
    credits_scraper(producers, "producer")
    credits_scraper(composers, "composer")
    credits_scraper(cinematographers, "cinematographer")
    credits_scraper(editors, "editor")

    kws = page_keywords_html.find_all('li', {'data-testid': "list-summary-item"})
    if kws:
        kw_list = [kw.find('a').text for kw in kws]
        keywords.append(kw_list)
    else:
        print("Empty value.")
        keywords.append(pd.NA)

    parental = page_parental_html.find('tr', {'id': "mpaa-rating"})
    if parental:
        mpaa_rating = parental.find_all("td")[1].text
        mpaa_ratings.append(mpaa_rating)
    else:
        print("Empty value.")
        mpaa_ratings.append(pd.NA)

    def tech_scraper(target_list, html_tag, spec):
        tech = page_technical_html.find("li", {'id': spec})
        if tech:
            params = tech.find_all(html_tag)
            target_list.append([param.text for param in params])
        else:
            print("Empty value.")
            target_list.append(pd.NA)

    tech_scraper(colors, "a", "colorations")
    tech_scraper(aspect_ratios, "span", "aspectratio")
    tech_scraper(sound_mixes, "a", "soundmixes")

    print(f"\nEnd of loop {count}")
    print("...\n")

end_time = datetime.now()
print("====================")
print("====================")
print("\t FINISHED")
print("total duration:" + str(end_time - start_time))
print("====================")
print("====================")

# Build and save csv file with the scraped data
scraped_films_df = pd.DataFrame()
scraped_films_df["Const"] = const
scraped_films_df["Title"] = title
scraped_films_df["URL"] = url
scraped_films_df["metacritic_score"] = metacritic_scores
scraped_films_df["top_cast"] = top_casts
scraped_films_df["writer"] = writers
scraped_films_df["producer"] = producers
scraped_films_df["composer"] = composers
scraped_films_df["cinematographer"] = cinematographers
scraped_films_df["editor"] = editors
scraped_films_df["country"] = countries
scraped_films_df["language"] = languages
scraped_films_df["company"] = companies
scraped_films_df["budget"] = budgets
scraped_films_df["gross_domestic"] = grosses_domestic
scraped_films_df["gross_domestic_opening_we"] = grosses_domestic_opening_we
scraped_films_df["gross_worldwide"] = grosses_ww
scraped_films_df["keywords"] = keywords
scraped_films_df["mpaa_rating"] = mpaa_ratings
scraped_films_df["color"] = colors
scraped_films_df["aspect_ratio"] = aspect_ratios
scraped_films_df["sound-mix"] = sound_mixes

# Don't overwrite by mistake!
scraped_films_df.to_csv('./scraped_data.csv', index=False)

# Set display options to avoid truncation
pd.set_option('display.max_columns', 30)   # Show all columns
pd.set_option('display.width', None)         # Don't wrap lines
pd.set_option('display.max_colwidth', None)  # Show full content of each column

print(scraped_films_df.head(10))  # Prints the first 10 rows
# Add scraped data to csv file holding ratings and other variables
if False:
    scraped_films = pd.read_csv("./scraped_data.csv")
    my_ratings = pd.read_csv("./ratings.csv")

    print(scraped_films.shape)
    print(my_ratings.shape)

    films = pd.merge(my_ratings, scraped_films)
    print(films.shape)

    films.to_csv('./ratings_extended.csv', index=False)
