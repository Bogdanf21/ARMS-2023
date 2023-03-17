import warnings

import requests
import time

from bs4 import BeautifulSoup

base_url = "https://www.justwatch.com/"
titles_url_en = "https://www.justwatch.com/us/tv-show/"
titles_url_ro = "https://www.justwatch.com/ro/seriale/"

accepted_platforms = [
    'Netflix',
    'HBO Max',
    'Disney Plus',
    'Amazon Prime'
]


def get_url_from_title(title, url=titles_url_en):
    parts = [part for part in title.split(" ") if part != "\n" and len(part)]
    new_url = url + "-".join(parts)
    print("URL:", new_url)
    return new_url


def get_platforms_from_title(title, title_base_url=titles_url_ro):
    """
    This needs to be separated from other scrapping because it depends on the region (in this case it is hardcoded
    with Romania :param title: :param title_base_url: If you want to get the streaming platforms from other country,
    give the root URL, for example https://www.justwatch.com/ro/seriale/ for Romania :return: list with the platforms
    that you can watch the show, ex: ["Netflix", "HBO GO"]
    """
    url = get_url_from_title(title, title_base_url)
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Status code: {response.status_code}')
    html = response.content

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Platforms
    # Find all relevant div tags and extract alt attributes if the span tag has content "Stream"
    platforms = set()
    for row in soup.find_all('div', class_='price-comparison__grid__row__holder'):
        title_div = row.find_previous_sibling('div', class_='price-comparison__grid__row__title')
        if title_div and title_div.find('span', class_='price-comparison__grid__row__title-label', string='Stream'):
            for img in row.find_all('img'):
                platforms.add(img['alt'])
    platforms = [p for p in platforms if p in accepted_platforms]
    return platforms


def get_genres_for_title(title):
    url = get_url_from_title(title, titles_url_en)
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Status code: {response.status_code}')
    html = response.content

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    genres_div = soup.find('div', class_='detail-infos__subheading', string='Genres')

    if genres_div:
        genres_value_div = genres_div.find_next_sibling('div', class_='detail-infos__value')
        if genres_value_div:
            genres_string = genres_value_div.text.strip()
            return genres_string.split(", ")
    raise Exception("Genres not found")


show = "Modern Family"

platform = get_platforms_from_title(show)
genres = get_genres_for_title(show)
print(platform)
print(genres)
