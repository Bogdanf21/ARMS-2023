import warnings
from time import sleep

from bs4 import BeautifulSoup
from urllib.parse import quote
import requests

suggestion_endpoint = "https://v3.sg.media-imdb.com/suggestion/x/{title}.json"
page_title_endpoint = "https://www.imdb.com/title/{id}"


HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


def get_titles_from_url(url, languages=None):
    if languages is None:
        languages = ["en-GB", "en", "en-US"]

    languages = ','.join(languages)
    headers = {
        'Accept-Language': languages + ';q=0.5'
    }
    
    response = requests.get(url, headers=headers)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the rows in the table and loop through them
    movies = []
    for row in soup.select("table tbody tr"):
        # Extract the title, year, and rating of the movie from the appropriate elements
        title = row.select_one("td.titleColumn a").get_text().strip()
        year = row.select_one("span.secondaryInfo").get_text().strip()[1:-1]
        rating = row.select_one("td.ratingColumn strong").get_text().strip()

        # Create a dictionary for the current movie and append it to the list of movies
        movies.append({"title": title, "year": year, "rating": rating})
    return movies


def get_page_url_from_title(title):
    title_formatted = quote(title).lower()
    endpoint = suggestion_endpoint.format(title=title_formatted)
    response = requests.get(endpoint)
    while response.status_code == 429:
        sleep(5)
        response = requests.get(endpoint)
    data = response.json()
    if response.status_code != 200:
        warnings.warn(f"Genres not found for title {title}")
        return ""

    try:
        for d in data["d"]:
            if d["l"] == title:
                return page_title_endpoint.format(id=d["id"])

    except Exception as e:
        print(e)
        return ""


def get_genres_for_title(title):
    session = requests.session()
    page_url = get_page_url_from_title(title)
    print(f"Page url for {title}: {page_url}")
    if page_url == "" or page_url is None:
        print("Couldn't get link; no genres found")
        return []
    response = session.get(page_url, headers=HEADERS)
    while response.status_code == 429:
        sleep(5)
        response = session.get(page_url, headers=HEADERS)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    try:
        # find the div tag with `data-testid="genres"` attribute
        genres_div = soup.find('div', {'data-testid': 'genres'})
        # extract every string in <span class="ipc-chip__text"> tags that are descendants of the genres_div
        genre_strings = [span.text for span in genres_div.find_all('span', {'class': 'ipc-chip__text'})]
    except Exception as e:
        print(e)
        return []
    return genre_strings
