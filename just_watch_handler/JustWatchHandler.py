import json
import time
import warnings
import requests

from bs4 import BeautifulSoup

import db.consts

search_titles = "https://apis.justwatch.com/graphql"

base_url = "https://www.justwatch.com"

accepted_platforms = db.consts.accepted_platforms


def title_search(title, language="en"):
    country = "US" if language == "en" else language.upper()

    session = requests.session()
    request_body = {"operationName": "GetSuggestedTitles",
                    "variables": {"country": country, "language": language, "first": 4,
                                  "filter": {"searchQuery": title}},
                    "query": "query GetSuggestedTitles($country: Country!, $language: Language!, $first: Int!, $filter: TitleFilter) {\n  popularTitles(country: $country, first: $first, filter: $filter) {\n    edges {\n      node {\n        ...SuggestedTitle\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SuggestedTitle on MovieOrShow {\n  id\n  objectType\n  objectId\n  content(country: $country, language: $language) {\n    fullPath\n    title\n    originalReleaseYear\n    posterUrl\n    fullPath\n    __typename\n  }\n  __typename\n}\n"}
    request_headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(search_titles, json=request_body, headers=request_headers)

    if response.status_code != 200:
        if response.status_code == 429:
            while response.status_code == 429:
                time.sleep(10)
                response = requests.post(search_titles, json=request_body, headers=request_headers)
        else:
            warnings.warn("could not request a title")
    response_dict = json.loads(response.content)
    if len(response_dict["data"]["popularTitles"]["edges"]) != 0:
        url_path = response_dict["data"]["popularTitles"]["edges"][0]["node"]["content"]["fullPath"]
        return url_path
    return None


def get_platforms_from_title(title, region="ro"):
    """
    This needs to be separated from other scrapping because it depends on the region (in this case it is hardcoded
    with Romania :param title: :param title_base_url: If you want to get the streaming platforms from other country,
    give the root URL, for example https://www.justwatch.com/ro/seriale/ for Romania :return: list with the platforms
    that you can watch the show, ex: ["Netflix", "HBO GO"]
    """
    region = region.lower()
    if region not in ["ro", "us"]:
        warnings.warn(f"Region {region} not supported")
        return

    url_title = base_url
    found_title = title_search(title, language="ro")
    if found_title is None:
        warnings.warn(f"Title {found_title} not found in suggestions")
        return {}
    url_title += found_title
    response = request_wrapper(f"requests.get(\"{url_title}\")")

    while response.status_code == 429:
        time.sleep(10)
        response = request_wrapper(f"requests.get(\"{url_title}\")")

    if response.status_code != 200:
        raise Exception(f'Could not find title {found_title}, {response}')

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
    return {"platforms": platforms,
            "region": region}


def get_info_for_title(title):
    try:
        info = {
            "genre": None,
            "rating": None,
            "number_of_reviews": None,
            "type": None
        }
        found_title = title_search(title)
        if found_title is None:
            print(f"The title {found_title} has not been found in suggestions")
            return {}
        url_title = base_url
        url_title += found_title

        response = request_wrapper(f"requests.get(\"{url_title}\")")
        while response.status_code == 429:
            time.sleep(10)
            response = request_wrapper(f"requests.get(\"{url_title}\")")

        if response.status_code != 200:
            raise Exception(f'Could not find info for title {found_title}, {url_title}')

        html = response.content
        info["type"] = "movie" if "movie" in response.url or "film" in response.url else "tv-show"

        soup = BeautifulSoup(html, "html.parser")

        # Genres
        genres = None
        genres_div = soup.find('div', class_='detail-infos__subheading', string='Genres')
        if genres_div:
            genres_value_div = genres_div.find_next_sibling('div', class_='detail-infos__value')
            if genres_value_div:
                genres_string = genres_value_div.text.strip()
                genres = genres_string.split(", ")

        if genres is None:
            warnings.warn(f"Genres not found for title {found_title}")
        else:
            info["genre"] = genres

        imdb_tag_content = None
        # The rating and number of reviews is in a tag, and it looks like "9.6 (408k)"
        # a_tag = soup.find('img', {'alt': 'IMDB'}).find_parent('a') if soup.find('img', {'alt': 'IMDB'}) else None
        a_tags = [t.find_parent('a') for t in soup.find_all('img', {'alt': 'IMDB'}) if soup.find('img', {'alt': 'IMDB'})]
        for t in a_tags:
            if t and 'IMDB' in t.find('img')['alt']:
                imdb_tag_content = t.text.strip()

        if imdb_tag_content is None:
            warnings.warn(f"Rating not found for title {found_title}")
        else:
            if len(imdb_tag_content.split(" ")) == 2:
                info["rating"], info["number_of_reviews"] = imdb_tag_content.split(" ")
            else:
                info["rating"] = imdb_tag_content

            if info["number_of_reviews"]:
                info["number_of_reviews"] = shorthand_to_number(info["number_of_reviews"][1:-1])  # [1:-1] gets rid of first
            # and last character, in our case "(" and ")"

        return info
    except Exception as e:
        print(e)


def get_title_object(title):
    info = get_info_for_title(title)
    plat = get_platforms_from_title(title)
    to_be_returned = {
        "title": title,
        **info,
        **plat
    }
    if len(to_be_returned.keys()) > 1:
        return to_be_returned
    return {}


def shorthand_to_number(string):
    if string[-1].lower() == 'k':
        return int(float(string[:-1]) * 1000)
    elif string[-1].lower() == 'm':
        return int(float(string[:-1]) * 1000000)
    else:
        return int(string)


def request_wrapper(request_as_string):
    response = None
    while response is None:
        try:
            response = eval(request_as_string)
        except Exception as e:
            warnings.warn(f"Request did not execute")
            print(e)
    return response


__all__ = ["get_info_for_title", "get_platforms_from_title", "get_title_object"]