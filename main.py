from just_watch_handler.JustWatchHandler import get_platforms_from_title, get_info_for_title


def get_title_info(title):
    platforms = get_platforms_from_title(title)
    info = get_info_for_title(title)

    return {
        "title": title,
        **info,
        "platforms": platforms
    }


if __name__ == '__main__':
    pass
