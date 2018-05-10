import os

from forex_python.converter import CurrencyRates
from tabler import CSV, Table


class Countries:

    def __init__(self):
        self.table = self.get_table()
        country_list = [Country(row) for row in self.table]
        self.countries = {int(country.id): country for country in country_list}

    def get_table(self):
        return Table(self.get_table_path(), table_type=CSV())

    def get_table_path(self):
        filename = 'cc_countries.csv'
        file_path = __file__
        directory = os.path.dirname(file_path)
        file_path = os.path.join(directory, filename)
        return file_path

    def __iter__(self):
        for country in self.countries.values():
            yield country

    def __getitem__(self, key):
        return self.countries[int(key)]


class Country:
    REST_OF_WORLD = 'ROW'
    EUROPE = 'EU'
    SERVICE_CODES = ('PAK', 'PAT', 'PAR', 'PAP', 'SMIU', 'SMIT')

    def __init__(self, row):
        self.row = row
        self.id = self.row['ID']
        self.name = self.row['Country']
        self.region = self.row['Region']
        self.iso_code = self.row['ISO Code']
        self.currency_code = self.row['Currency'] or None
        self.min_channel_fee_local = float(self.row['Min Channel Fee'])
        if self.currency_code is None or self.currency_code == 'GBP':
            self.currency_rate = 1
        else:
            self.currency_rates = CurrencyRates()
            self.currency_rate = self.currency_rates.get_rate(
                str(self.currency_code), 'GBP')
        self.services = {
            service: Service(row[service + ' Item'], row[service + ' KG']) for
            service in self.SERVICE_CODES if row[service + ' Item']}
        self.min_channel_fee = self.get_min_channel_fee()

    def get_min_channel_fee(self):
        if self.currency_code is None:
            return 0
        return int((self.min_channel_fee_local * self.currency_rate) * 100)

    def __repr__(self):
        return self.name

    def __getitem__(self, key):
        return self.services[key]


class Service:

    def __init__(self, item_price, kg_price):
        self.item_price = int(item_price)
        self.kg_price = int(kg_price)

    def calculate_price(self, weight):
        return self.item_price + self.calculate_weight_price(weight)

    def calculate_weight_price(self, weight):
        return int(weight / 1000 * self.kg_price)
