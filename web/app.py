import os
import sys
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from database import db_session, init_db, add_weather_card_to_db, db_delete_weater_card
from models import WeatherCard, weather_state_calc, make_weather_dict

WEATHER_API = 'http://api.openweathermap.org/data/2.5/weather'
API_KEY = os.environ.get('API_KEY')

init_db()

sentry_sdk.init(
    dsn="https://64342bad6e844f65839ab882f69d701e@o1148954.ingest.sentry.io/6220499",
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

app = Flask(__name__)
CORS(app)
app.config.from_object('settings')


def get_weather(city, country):
    """
    City weather search that gets weather from openweathermap.org API for Us based cities
    :param String city: the US city to query
    :return Tuple (String City, String State):  State is option of Chilly, Mild, Hot
    """
    wr = None
    weather_params = {'appid': API_KEY, 'q': f'{city} , {country}', 'units': 'metric'}
    try:
        wr = requests.get(WEATHER_API, params=weather_params)
        wr.raise_for_status()
    except requests.exceptions.RequestException as e:
        sentry_sdk.capture_exception(e)
        raise
    else:
        wr_data = wr.json()
        temp_c = wr_data.get('main').get('temp')
        state = weather_state_calc(temp_c)
    return temp_c, state


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        city_history = WeatherCard.query.all()
        city_weather_history_list = []  # pass weather dict to index template
        for city in city_history:
            try:
                temp_c, weather_state = get_weather(city.city_name, city.country_name)
            except requests.HTTPError:
                flash('API ERROR!')
                redirect('/', 404)
            else:
                weather_dict = make_weather_dict(city.city_name, city.id, weather_state, temp_c)
                city_weather_history_list.append(weather_dict)
        return render_template('index.html', city_weather_history_list=city_weather_history_list)

    elif request.method == 'POST':
        # if request.form['city_name'] == '':
        #     flash("The city doesn't exist!", "info")
        # else:
        wc = WeatherCard(city_name=request.form['city_name'])
        try:
            get_weather(wc.city_name, wc.country_name)
            add_weather_card_to_db(wc)
        except IntegrityError as ke:
            sentry_sdk.capture_exception(ke)
            flash('The city has already been added to the list!')
            return redirect('/')
        except KeyError as ie:
            sentry_sdk.capture_exception(ie)
            flash("The city doesn't exist!")
            return redirect('/')
        except requests.exceptions.HTTPError as he:
            sentry_sdk.capture_exception(he)
            flash("The city doesn't exist!")
            return redirect('/')
        return redirect(url_for('index'))


@app.route('/delete/<city_id>', methods=['POST', 'GET'])
def delete(city_id):
    wc = WeatherCard.query.filter_by(id=city_id).first()
    db_delete_weater_card(wc)
    return redirect('/')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port, debug=True)
    else:
        app.run(debug=True)
