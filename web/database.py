from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

#
engine = create_engine('sqlite:///Weather App/task/web/weather.db', connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import yourapplication.models

    from models import WeatherCard
    Base.metadata.create_all(bind=engine)


def add_weather_card_to_db(wc):
    """
    Adds the users queried city to the database
    :raises IntegrityError, KeyError
    :param wc:
    :return:
    """
    db_session.add(wc)
    db_session.commit()


def db_delete_weater_card(wc):
    db_session.delete(wc)
    db_session.commit()