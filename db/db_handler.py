import sqlite3
import threading
import warnings

from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

import db.consts
from db.consts import accepted_platforms

engine = create_engine('sqlite:///database.db')
Session = scoped_session(sessionmaker(bind=engine))


class TitlesDB:
    def __init__(self):
        # Connect to the database
        # self.conn = sqlite3.connect('database.db')
        # self.c = self.session.cursor()
        self.session = Session()

        # Create the titles table if it doesn't exist
        self.session.execute(text(db.consts.create_table_titles))

        # Create the platforms table if it doesn't exist
        self.session.execute(text(db.consts.create_table_platforms))

        self.session.execute(text(db.consts.create_table_genres))

        # Create the title_platforms table if it doesn't exist
        self.session.execute(text(db.consts.create_table_title_platforms))

        self.session.execute(text(db.consts.create_table_title_genres))

        # Add platforms if they don't exist
        for platform in accepted_platforms:
            self.session.execute(
                text(db.consts.insert_platform.format(platform)))
        self.session.commit()
        self.lock = threading.Lock()

    def add_title(self, title_dict):
        title = title_dict["title"]
        if title is None:
            warnings.warn(f"Title is none for {title_dict}")
            return

        # Check if title already exists in database
        result = self.session.execute(
            text("SELECT * FROM titles WHERE title = \"{}\"".format(title)))

        existing_title = result.fetchone()

        # If title doesn't exist, enter it
        if not existing_title:
            keys = ["title", "type", "rating", "number_of_reviews"]
            title_keys = ', '.join(keys)
            title_vals = tuple([title_dict[k] for k in keys])
            title_query = "INSERT INTO titles ({}) VALUES ({})".format(title_keys, ', '.join([f'"{val}"' for val in title_vals]))
            result = self.session.execute(text(title_query))
            title_id = result.lastrowid
        else:
            title_id = existing_title[0]

        # Insert the platforms into the platforms table if they don't already exist
        platform_ids = []
        for platform in title_dict.get('platforms', []):
            result = self.session.execute(text(db.consts.get_platform_id.format(platform)))
            platform_id = result.fetchone()
            if platform_id is not None:
                platform_ids.append(platform_id[0])

        # Insert the title-platform associations into the title_platforms table
        for platform_id in platform_ids:
            self.session.execute(text(
                db.consts.insert_title_platforms.format(title_id, platform_id,title_dict["region"])))

        # Insert new genres into the genres table if they don't already exist
        genre_ids = []
        for genre in title_dict.get('genre', []):
            result = self.session.execute(text(db.consts.get_genre_id.format(genre)))
            genre_id = result.fetchone()
            if genre_id is None:
                result = self.session.execute(text(db.consts.insert_genre.format(genre)))
                genre_id = result.lastrowid
            else:
                genre_id = genre_id[0]
            genre_ids.append(genre_id)
        # Insert the title-genre associations into the title_genres table
        for genre_id in genre_ids:
            self.session.execute(
                text(db.consts.insert_title_genres.format(title_id, genre_id)))
        self.session.commit()

    def remove_title(self, title):
        try:
            # Delete the title from the titles table and the associated rows from the title_platforms table
            self.session.execute(text(db.consts.delete_title.format(title)))
            self.session.execute(text("DELETE FROM title_platforms WHERE title_id NOT IN (SELECT id FROM titles)"))
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()
