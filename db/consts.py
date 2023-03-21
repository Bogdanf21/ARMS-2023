accepted_platforms = [
    'Netflix',
    'HBO Max',
    'Disney Plus'
]

title_pages = [
    "https://www.imdb.com/chart/top/",
    "https://www.imdb.com/chart/toptv/"
]

create_table_titles = '''CREATE TABLE IF NOT EXISTS titles
                         (id INTEGER PRIMARY KEY, title TEXT UNIQUE, type TEXT, rating INTEGER, number_of_reviews INTEGER)'''
get_title = '''SELECT * FROM titles WHERE title = \"{}\"'''
insert_title = "INSERT INTO titles ({}) VALUES ({})"
delete_title = "DELETE FROM titles WHERE title = \"{}\""

create_table_platforms = '''CREATE TABLE IF NOT EXISTS platforms
                          (id INTEGER PRIMARY KEY, name TEXT UNIQUE)'''
get_platform_id = '''SELECT id FROM platforms WHERE name=\"{}\"'''
insert_platform = "INSERT OR IGNORE INTO platforms (name) VALUES (\"{}\")"

create_table_genres = '''CREATE TABLE IF NOT EXISTS genres
                     (id INTEGER PRIMARY KEY, name TEXT UNIQUE)'''
get_genre_id = "SELECT id FROM genres WHERE name =\"{}\""
insert_genre = "INSERT INTO genres (name) VALUES (\"{}\")"

create_table_title_platforms = '''CREATE TABLE IF NOT EXISTS title_platforms
                          (title_id INTEGER, platform_id INTEGER, region TEXT,
                           FOREIGN KEY(title_id) REFERENCES titles(id) ON DELETE CASCADE,
                           FOREIGN KEY(platform_id) REFERENCES platforms(id),
                           UNIQUE(title_id, platform_id, region) ON CONFLICT IGNORE)'''
insert_title_platforms = "INSERT INTO title_platforms (title_id, platform_id, region) VALUES (\"{}\", \"{}\", \"{}\")"

create_table_title_genres = '''CREATE TABLE IF NOT EXISTS title_genres
                          (title_id INTEGER, genre_id INTEGER,
                           FOREIGN KEY(title_id) REFERENCES titles(id) ON DELETE CASCADE,
                           FOREIGN KEY(genre_id) REFERENCES genres(id),
                           UNIQUE(title_id, genre_id) ON CONFLICT IGNORE)'''
insert_title_genres = "INSERT INTO title_genres (title_id, genre_id) VALUES (\"{}\", \"{}\")"




# create_titles = '''CREATE TABLE titles
#                  (id INTEGER PRIMARY KEY, title TEXT, type TEXT, genre TEXT, rating INTEGER, number_of_reviews INTEGER)'''
#
# create_platforms = '''CREATE TABLE platforms
#                  (id INTEGER PRIMARY KEY, name TEXT)'''
#
# create_title_platforms = '''CREATE TABLE title_platforms
#                  (title_id INTEGER, platform_id INTEGER,
#                   FOREIGN KEY(title_id) REFERENCES titles(id),
#                   FOREIGN KEY(platform_id) REFERENCES platforms(id))'''
#
# add_platform = '''INSERT INTO platforms (name) VALUES ('{platform}')'''
#
# add_title = '''INSERT INTO titles (id, title, type, genre, rating, number_of_reviews) values ('{id}', '{title}', '{type}', '{genre}', '{rating}', '{number_of_reviews}')'''
#

