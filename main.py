import concurrent.futures
import json
import imdb_handler.ImdbHandler

from multiprocessing.pool import ThreadPool as Pool
from just_watch_handler.JustWatchHandler import get_platforms_from_title, get_info_for_title

titles = [
    "https://www.imdb.com/chart/top/",
    "https://www.imdb.com/chart/toptv/"
]
titles_file_path = "./db/titles.txt"
titles_info_file_path = "./db/titles_info.txt"

pool_size = 10


def get_title_info(title):
    platforms = get_platforms_from_title(title)
    info = get_info_for_title(title)

    return {
        "title": title,
        **info,
        "platforms": platforms
    }


if __name__ == '__main__':
    # Get titles
    titles = imdb_handler.ImdbHandler.get_titles_from_url(titles[1])
    file = open(titles_file_path, "w")
    titles = [t["title"] for t in titles]
    file.write(json.dumps(titles))
    file.close()

    titles_file = open(titles_file_path, 'r')
    contents = titles_file.read()
    print("Contents:", contents)
    titles_list = json.loads(contents)
    print("titles:", titles_list)

    infos = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        title_futures = [executor.submit(get_title_info, title) for title in titles]

        for future in concurrent.futures.as_completed(title_futures):
            title_info = future.result()
            print("Infos:", title_info)
            infos.append(title_info)

    # infos = []
    # for title in titles_list:
    #     title_info = get_title_info(title)
    #     infos.append(title_info)
    #     print("Infos:", title_info)

    titles_info_file = open(titles_info_file_path, "w")
    titles_info_file.write(str(infos))
    titles_info_file.close()
