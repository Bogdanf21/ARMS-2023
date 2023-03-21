import concurrent
import json
import sqlite3
import time
import warnings

import imdb_handler.ImdbHandler
from db.consts import title_pages
from db.db_handler import TitlesDB
from just_watch_handler.JustWatchHandler import get_platforms_from_title, get_info_for_title, get_title_object


if __name__ == "__main__":
    start_time = time.time()
    for page in title_pages:
        title_dicts = imdb_handler.ImdbHandler.get_titles_from_url(page)
        title_dicts = [t["title"] for t in title_dicts]
        for title in title_dicts:
            db = TitlesDB()
            title_dict = get_title_object(title)
            if len(title_dict.keys()) == 0:
                warnings.warn(f"Title {title} not found")
                continue
            db.add_title(title_dict)
            print("added title ", title_dict)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")

