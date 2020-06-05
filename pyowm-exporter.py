#!/usr/bin/env python3
# By Lance Zeligman

from pyowm import OWM
from prometheus_client import Enum, Gauge, Info, start_http_server
from prometheus_client.core import REGISTRY
from time import sleep
import configparser
import logging
import os
import sys

# Create logger
logger = logging.getLogger("pyowm-exporter")
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")
c_handler.setFormatter(formatter)
logger.addHandler(c_handler)

# Array of all possible status values
states = [
    "thunderstorm with light rain",
    "thunderstorm with rain",
    "thunderstorm with heavy rain",
    "light thunderstorm",
    "thunderstorm",
    "heavy thunderstorm",
    "ragged thunderstorm",
    "thunderstorm with light drizzle",
    "thunderstorm with drizzle",
    "thunderstorm with heavy drizzle",
    "light intensity drizzle",
    "drizzle",
    "heavy intensity drizzle",
    "light intensity drizzle rain",
    "drizzle rain",
    "heavy intensity drizzle rain",
    "shower rain and drizzle",
    "heavy shower rain and drizzle",
    "shower drizzle",
    "light rain",
    "moderate rain",
    "heavy intensity rain",
    "very heavy rain",
    "extreme rain",
    "freezing rain",
    "light intensity shower rain",
    "shower rain",
    "heavy intensity shower rain",
    "ragged shower rain",
    "light snow",
    "Snow",
    "Heavy snow",
    "Sleet",
    "Light shower sleet",
    "Shower sleet",
    "Light rain and snow",
    "Rain and snow",
    "Light shower snow",
    "Shower snow",
    "Heavy shower snow",
    "mist",
    "Smoke",
    "Haze",
    "sand/ dust whirls",
    "fog",
    "sand",
    "dust",
    "volcanic ash",
    "squalls",
    "tornado",
    "clear sky",
    "few clouds",
    "scattered clouds",
    "broken clouds",
    "overcast clouds",
]

# Create the enum object with all possible status values
# as states
weather_state = Enum(
    "pyowm_current_weather_state", "Current Weather State", states=states
)

temperature = Gauge(
    "pyowm_current_temperature_metric",
    "Current Temperature in Metric",
    ["system", "data"],
)

cloudiness_rate = Gauge("pyowm_cloudiness", "Current Cloudiness percentage")
wind = Gauge("pyowm_wind", "Current Wind Data", ["metric_type"])
humidity_rate = Gauge("pyowm_humidity", "Current Humidity Percentage")
pressure = Gauge("pyowm_pressure", "Current Pressure Data", ["metric_type"])
rain = Gauge("pyowm_rain", "Current Rain Data", ["metric_type"])
snow = Gauge("pyowm_snow", "Current Snow Data")
sun = Gauge("pyowm_sun", "Sun Rise and Sun Set Time Info", ["metric_type"])


def getconfigpath():
    """
    Returns the path for the config
    """

    path = os.path.join(sys.path[0], "config", "pyowm-exporter.cfg")
    return path


def readconfig():
    """
    reads the config for zz-8
    """

    configpath = getconfigpath()
    config = configparser.RawConfigParser()
    config.read(configpath)
    if not config.sections():
        return False
    appconfig = {}
    appconfig["api_key"] = config.get("prod", "api_key")

    return appconfig


class WeatherExporter(object):
    """
  weather_exporter [summary]

  This class pulls in the open weather data and 
  creates the prometheus exporter object
  """

    def __init__(self, mgr):
        """
        __init__ pulls in the open weather object and config
        """
        # Set the class variables
        self.logger = logging.getLogger("pyowm-exporter")

        # Set the location for our weather
        try:
            observation = mgr.weather_at_place("herndon, virginia")
            self.logger.info("Obtained weather data")
        except Exception as ex:
            self.logger.critical(f"Encountered unexpected error\n{ex}")
            sys.exit(1)

        self.logger.info("Populating the Metrics")
        self.collect(observation)
        self.logger.info("Metrics Populated")

    # @weather_state
    def generate_weather_states(self, weather):
        """
        weatherstates Generates the weather_state num

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """

        # Set the current weather status
        weather_state.state(weather.detailed_status)

    def generate_temperature(self, weather):
        """
        generate_temperature [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        temperature.labels(system="celsius", data="temp").set(
            weather.temperature("celsius")["temp"]
        )

        temperature.labels(system="celsius", data="temp_max").set(
            weather.temperature("celsius")["temp_max"]
        )

        temperature.labels(system="celsius", data="temp_min").set(
            weather.temperature("celsius")["temp_min"]
        )

        temperature.labels(system="celsius", data="feels_like").set(
            weather.temperature("celsius")["feels_like"]
        )

        temperature.labels(system="fahrenheit", data="temp").set(
            weather.temperature("fahrenheit")["temp"]
        )

        temperature.labels(system="fahrenheit", data="temp_max").set(
            weather.temperature("fahrenheit")["temp_max"]
        )

        temperature.labels(system="fahrenheit", data="temp_min").set(
            weather.temperature("fahrenheit")["temp_min"]
        )

        temperature.labels(system="fahrenheit", data="feels_like").set(
            weather.temperature("fahrenheit")["feels_like"]
        )

        temperature.labels(system="kelvin", data="temp").set(
            weather.temperature("kelvin")["temp"]
        )

        temperature.labels(system="kelvin", data="temp_max").set(
            weather.temperature("kelvin")["temp_max"]
        )

        temperature.labels(system="kelvin", data="temp_min").set(
            weather.temperature("kelvin")["temp_min"]
        )

        temperature.labels(system="kelvin", data="feels_like").set(
            weather.temperature("kelvin")["feels_like"]
        )

    def generate_clouds(self, weather):
        """
        generate_clouds [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        cloudiness_rate.set(weather.clouds)

    def generate_wind(self, weather):
        """
        generate_wind [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        wind.labels(metric_type="wind_speed").set(weather.wind()["speed"])
        wind.labels(metric_type="wind_direction").set(weather.wind()["deg"])

    def generate_humidity(self, weather):
        """
        generate_humidity [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        humidity_rate.set(weather.humidity)

    def generate_pressure(self, weather):
        """
        generate_pressure [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        pressure.labels(metric_type="press").set(weather.pressure["press"])

    def generate_rain(self, weather):
        """
        generate_rain [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        try:
            rain.labels(metric_type="1 hour").set(weather.rain["1h"])
        except:
            rain.labels(metric_type="1 hour").set(0)

        try:
            rain.labels(metric_type="3 hour").set(weather.rain["3h"])
        except:
            rain.labels(metric_type="3 hour").set(0)

    def generate_snow(self, weather):
        """
        generate_snow [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        try:
            snow.set(weather.snow["all"])
        except:
            snow.set(0)

    def generate_sun_data(self, weather):
        """
        generate_sun_data [summary]

        :param weather: Pyowm class object containing current weather information
        :type weather: pyowm.weatherapi25.weather.Weather()
        :return: Returns true
        :rtype: Bool
        """
        sun.labels(metric_type="Sunset").set(weather.sset_time)
        sun.labels(metric_type="Sunrise").set(weather.srise_time)

    def collect(self, observation):
        """
        collect Collect calls all of the generate methods
        """
        weather = observation.weather

        self.generate_weather_states(weather)

        self.generate_temperature(weather)

        self.generate_clouds(weather)

        self.generate_wind(weather)

        self.generate_humidity(weather)

        self.generate_pressure(weather)

        self.generate_rain(weather)

        self.generate_snow(weather)

        self.generate_sun_data(weather)


if __name__ == "__main__":
    config = readconfig()
    owm = OWM(config["api_key"])
    mgr = owm.weather_manager()
    start_http_server(9119)

    while True:
        WeatherExporter(mgr)
        sleep(15)
