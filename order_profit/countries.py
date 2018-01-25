import os

from tabler import Tabler as Table


class Countries:

    def __init__(self):
        self.table = self.get_table()
        country_list = [Country(row) for row in self.table]
        self.countries = {int(country.id): country for country in country_list}

    def get_table(self):
        return Table(filename=self.get_table_path())

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

    def __init__(self, row):
        self.row = row
        self.id = self.row['ID']
        self.name = self.row['Country']
        self.region = self.row['Region']
        self.iso_code = self.row['ISO Code']
        self.services = {
            service: Service(row[service + ' Item'], row[service + ' KG']) for
            service in ('PAK', 'PAT', 'PAR', 'PAP') if row[service + ' Item']}

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
