from sqlite3 import IntegrityError

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

import db.consts

engine = create_engine(f"sqlite:///database.db")
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class Title(Base):
    __tablename__ = 'titles'

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    type = Column(String)
    rating = Column(Integer)
    number_of_reviews = Column(Integer)

    genres = relationship('Genre', secondary='title_genres', back_populates='titles')
    platforms = relationship('Platform', secondary='title_platforms', back_populates='titles')


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    titles = relationship('Title', secondary='title_genres', back_populates='genres')


class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    titles = relationship('Title', secondary='title_platforms', back_populates='platforms')


class TitleGenre(Base):
    __tablename__ = 'title_genres'

    id = Column(Integer, primary_key=True)
    title_id = Column(Integer, ForeignKey('titles.id', ondelete='CASCADE'))
    genre_id = Column(Integer, ForeignKey('genres.id'))

    __table_args__ = (UniqueConstraint('title_id', 'genre_id', name='_title_genre_uc'),)


class TitlePlatform(Base):
    __tablename__ = 'title_platforms'

    id = Column(Integer, primary_key=True)
    title_id = Column(Integer, ForeignKey('titles.id', ondelete='CASCADE'))
    platform_id = Column(Integer, ForeignKey('platforms.id'))
    region = Column(String)

    __table_args__ = (UniqueConstraint('title_id', 'platform_id', 'region', name='_title_platform_uc'),)


class Database:
    def __init__(self):
        self.session = Session()

    def add_title(self, title_dict):
        # Start a new transaction
        self.session.begin()

        try:
            # Retrieve the title with a SELECT FOR UPDATE statement
            title = self.session.query(Title).filter(Title.title == title_dict['title']).with_for_update().first()

            if title:
                print(f"Title {title_dict['title']} already in database")
                return
                # Create a new title if it doesn't exist
            title = Title(title=title_dict['title'], type=title_dict['type'],
                          rating=title_dict['rating'] if title_dict['rating'] is not None else "",
                          number_of_reviews=title_dict['number_of_reviews'])
            self.session.add(title)

            # Add new genre and platform associations
            for genre_name in title_dict['genre']:
                genre = self.session.query(Genre).filter(Genre.name == genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    self.session.add(genre)
                    genre = self.session.query(Genre).filter(Genre.name == genre_name).first()
                title_genre = TitleGenre(title_id=title.id, genre_id=genre.id)
                self.session.add(title_genre)

            for platform_name in title_dict.get('platforms', []):
                region = title_dict['region']
                platform = self.session.query(Platform).filter(Platform.name == platform_name).first()
                if not platform:
                    platform = Platform(name=platform_name)
                    self.session.add(platform)
                    platform = self.session.query(Platform).filter(Platform.name == platform_name).first()
                title_platform = TitlePlatform(title_id=title.id, platform_id=platform.id, region=region)
                self.session.add(title_platform)

            # Commit the transaction
            self.session.commit()
            print("added title ", title_dict)
        except IntegrityError as e:
            # Rollback the transaction on integrity errors
            self.session.rollback()
            raise ValueError("Title already exists")

    def delete_title(self, title_name):
        title = self.session.query(Title).filter(Title.title == title_name).first()
        if not title:
            raise ValueError("Title not found")

        self.session.delete(title)
        self.session.commit()

    def find_title_by_name(self, title_name):
        title = self.session.query(Title).filter(Title.title == title_name).first()
        if not title:
            return None

        result = {'title': title.title, 'type': title.type}
        if title.rating is not None:
            result['rating'] = title.rating
        if title.number_of_reviews is not None:
            result['number_of_reviews'] = title.number_of_reviews

        genres = [tg.genre.name for tg in title.title_genres]
        result['genres'] = genres

        platforms = [{'name': tp.platform.name, 'region': tp.region} for tp in title.title_platforms]
        result['platforms'] = platforms

        return result

    def add_genre(self, genre_name):
        genre = self.session.query(Genre).filter(Genre.name == genre_name).first()
        if genre:
            raise ValueError("Genre already exists")

        genre = Genre(name=genre_name)
        self.session.add(genre)
        self.session.commit()

    def create(self):
        # Create the titles table if it doesn't exist
        self.session.execute(text(db.consts.create_table_titles))

        # Create the platforms table if it doesn't exist
        self.session.execute(text(db.consts.create_table_platforms))

        self.session.execute(text(db.consts.create_table_genres))

        # Create the title_platforms table if it doesn't exist
        self.session.execute(text(db.consts.create_table_title_platforms))

        self.session.execute(text(db.consts.create_table_title_genres))

        # Add platforms if they don't exist
        for platform in db.consts.accepted_platforms:
            self.session.execute(
                text(db.consts.insert_platform.format(platform)))
        self.session.commit()


def find_title(session, title_name):
    title = session.query(Title).filter_by(title=title_name).one()
    return title
