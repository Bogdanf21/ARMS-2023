from bs4 import BeautifulSoup
import requests


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


# # print(get_titles_from_URL("https://www.imdb.com/chart/top/"))
# print(get_titles_from_url("https://www.imdb.com/chart/toptv/"))
