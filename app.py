import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city')
    units = request.args.get('units')

    result_json = get_weather_info(city, units)

    icon_code = result_json['weather'][0]['icon']
    icon_url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'

    context = {
        'date': datetime.now(),
        'city': city,
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units),
        'icon_url': icon_url,
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    city1_result = get_weather_info(city1, units)
    city2_result = get_weather_info(city2, units)
    
    temp_difference = round((city1_result['main']['temp'] - city2_result['main']['temp']), 1)
    hum_difference = round((city1_result['main']['humidity'] - city2_result['main']['humidity']), 0)
    wind_difference = round((city1_result['wind']['speed'] - city2_result['wind']['speed']), 2)
    sunset_difference = round(((city1_result['sys']['sunset'] - city2_result['sys']['sunset']) / 3600), 1)

    context = {
        'date': datetime.now(),
        'units_letter': get_letter_for_units(units),
        'temp_difference': temp_difference,
        'hum_difference': hum_difference,
        'wind_difference': wind_difference,
        'sunset_difference': sunset_difference,
        'city1_info': {
            'city': city1,
            'description': city1_result['weather'][0]['description'],
            'temp': city1_result['main']['temp'],
            'humidity': city1_result['main']['humidity'],
            'wind_speed': city1_result['wind']['speed'],
            'sunrise': datetime.fromtimestamp(city1_result['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(city1_result['sys']['sunset']),
        },
        'city2_info': {
            'city': city2,
            'description': city2_result['weather'][0]['description'],
            'temp': city2_result['main']['temp'],
            'humidity': city2_result['main']['humidity'],
            'wind_speed': city2_result['wind']['speed'],
            'sunrise': datetime.fromtimestamp(city2_result['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(city2_result['sys']['sunset']),
        },
    }

    return render_template('comparison_results.html', **context)

def get_weather_info(city, units):
    '''
    Takes a city name and the desired units; makes a call to the OpenWeatherAPI
    and returns the results as a python dictionary
    '''
    params = {
        'q': city,
        'appid': API_KEY,
        'units': units,
    }

    return requests.get(API_URL, params=params).json()

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
