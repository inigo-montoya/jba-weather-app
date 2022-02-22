from sqlalchemy import Column, Integer, String
from database import Base


def make_weather_dict(city_name, city_id, weather_state, temp_c):
    # TODO add time of day background
    return {'city_name': city_name, 'city_id': city_id, 'weather_state': weather_state, 'temp_c': temp_c}


def weather_state_calc(temp, unit_of_measure='c'):
    state = ''
    if unit_of_measure == 'c':
        if temp < 10:
            state = 'Chilly'
        elif 10 < temp < 25:
            state = 'Mild'
        else:
            state = 'Hot'
    elif unit_of_measure == 'f':
        if temp < 32:
            state = 'Chilly'
        elif 32 < temp < 75:
            state = 'Mild'
        else:
            state = 'Hot'

    return state


class WeatherCard(Base):
    __tablename__ = 'weather_cards'

    id = Column(Integer, autoincrement=True, primary_key=True)
    city_name = Column(String(50), unique=True, nullable=False)
    country_name = Column(String(3), default='US')
    # weather_state = Column(String(30))

    def __init__(self, city_name=None, country_name='US'):
        self.city_name = city_name
        self.country_name = country_name

    def __repr__(self):
        return f'<Weather Card {self.city_name}, {self.country_name}'
