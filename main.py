import sys
import requests
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from datetime import datetime, timedelta


class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('weather.ui', self)
        self.weatherButton.clicked.connect(self.get_weather)
        self.clearButton.clicked.connect(self.clear)
        self.city_list.itemClicked.connect(self.load_city_weather)
        self.days_list.itemClicked.connect(self.load_day_forecast)
        self.removeCity_Button.clicked.connect(self.remove_city)
        self.cities = []

        self.load_cities()

        self.update_days_list()

    def get_weather(self):
        city = self.cityName.text()
        if city and city not in self.cities:
            if len(self.cities) >= 7:
                self.cities.pop(0)
            self.cities.append(city)
            self.city_list.addItem(city)

            self.save_cities()

        api_key = '506715da5e094a5d2f6a9650c95267d0'
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            forecast_items = data['list']
            forecasts = []
            today = datetime.now().strftime('%d.%m')

            for item in forecast_items:
                original_date = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                formatted_date = original_date.strftime('%d.%m')
                if formatted_date == today:
                    temperature = item['main']['temp']
                    weather_main = item['weather'][0]['main']
                    weather_description = item['weather'][0]['description']
                    time = item['dt_txt'].split(' ')[1]
                    forecasts.append(f'{time}: {temperature}°C, {weather_main} ({weather_description})')

            self.weather_res.clear()
            self.weather_res.addItems(forecasts)
        else:
            self.weather_res.clear()
            self.weather_res.addItem('Failed to find such city!')

    def clear(self):
        self.cityName.clear()
        self.weather_res.clear()

    def load_city_weather(self, item):
        city = item.text()
        self.cityName.setText(city)
        self.get_weather()

    def update_days_list(self):
        today = datetime.now()
        self.days_list.clear()
        for i in range(6):
            date = today + timedelta(days=i)
            self.days_list.addItem(date.strftime('%d.%m'))

    def load_day_forecast(self, item):
        date_str = item.text()
        city = self.cityName.text()
        if city:
            self.get_forecast_for_date(city, date_str)

    def get_forecast_for_date(self, city, date):
        api_key = '506715da5e094a5d2f6a9650c95267d0'
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            forecast_items = data['list']
            forecasts = []
            for item in forecast_items:
                original_date = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                formatted_date = original_date.strftime('%d.%m')
                if formatted_date == date:
                    temperature = item['main']['temp']
                    weather_main = item['weather'][0]['main']
                    weather_description = item['weather'][0]['description']
                    time = item['dt_txt'].split(' ')[1]
                    forecasts.append(f'{time}: {temperature}°C, {weather_main} ({weather_description})')

            self.weather_res.clear()
            self.weather_res.addItems(forecasts)
        else:
            self.weather_res.clear()
            self.weather_res.addItem('Failed to retrieve forecast.')

    def remove_city(self):
        city = self.cityName.text()
        if city in self.cities:
            self.cities.remove(city)

            self.city_list.clear()
            self.city_list.addItems(self.cities)
            self.cityName.clear()
            self.weather_res.clear()

            self.save_cities()

    def save_cities(self):
        with open('cities.pkl', 'wb') as f:
            pickle.dump(self.cities, f)

    def load_cities(self):
        try:
            with open('cities.pkl', 'rb') as f:
                self.cities = pickle.load(f)
                self.city_list.addItems(self.cities)
        except (FileNotFoundError, EOFError):
            self.cities = []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
