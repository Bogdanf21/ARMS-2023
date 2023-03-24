import time
import warnings
import concurrent.futures
import imdb_handler.ImdbHandler
from db.consts import title_pages
from db.db_orm import Database
from just_watch_handler.JustWatchHandler import get_title_object


def process_title(title):
    db = Database()
    title_dict = get_title_object(title)
    if len(title_dict.keys()) == 0:
        warnings.warn(f"Title {title} not found")
        return
    db.add_title(title_dict)


if __name__ == "__main__":
    db_create = Database()
    db_create.create()

    start_time = time.time()
    for page in title_pages:
        title_dicts = imdb_handler.ImdbHandler.get_titles_from_url(page)
        title_dicts = [t["title"] for t in title_dicts]
        print(title_dicts)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_title, item) for item in title_dicts]
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")
