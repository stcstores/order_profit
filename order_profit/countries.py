"""Load informatio about shipping destinations from cc_countries.csv."""

import os

import requests
from tabler import CSV, Table


class Countries:
    """
    Container for country shipping information.

    Country information is loaded from data in a .csv file named
    'cc_countries.csv' in the same directory as this file.
    """

    def __init__(self):
        """
        Store country data in self.countries.

        Country information is loaded from data in a .csv file named
        'cc_countries.csv' in the same directory as this file.

        self.countries is a dict of country IDs to Country objects
        """
        self.table = self.get_table()
        country_list = [Country(row) for row in self.table]
        self.countries = {int(country.id): country for country in country_list}

    def get_table(self):
        """Return tabler.Table object containing country information."""
        return Table(self.get_table_path(), table_type=CSV())

    def get_table_path(self):
        """Return full path to country data .csv."""
        filename = "cc_countries.csv"
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
    """
    Container for country information.

    Attributes:
        row: Table row from which data is loaded.
        id: The Cloud Commerce Country ID of the country.
        name: The name of the country.
        region: 'EU' or 'ROW'; Europe or Rest of World.
        iso_code: Two digit ISO code for the country.
        currency_code: The currency used in the country. e.g 'GBP'.
        currency_rate: The rate of the countries currrency to GBP.
        min_channel_fee: The minimum fee charged by selling channels
            in this country.
        services: Dict of shipping services available to this country as
            order_profit.countries.Service objects.

    """

    REST_OF_WORLD = "ROW"
    EUROPE = "EU"
    SERVICE_CODES = ("PAK", "PAT", "PAR", "PAP", "SMIU", "SMIT")

    _currency_rate = None

    def __init__(self, row):
        """
        Load country information from table row.

        Args:
            row: Table row from 'countries.csv'.

        """
        self.row = row
        self.id = int(self.row["ID"])
        self.name = self.row["Country"]
        self.region = self.row["Region"]
        self.iso_code = self.row["ISO Code"]
        self.currency_code = self.row["Currency"] or None
        self.min_channel_fee_local = float(self.row["Min Channel Fee"])
        self.services = {
            service: Service(row[service + " Item"], row[service + " KG"])
            for service in self.SERVICE_CODES
            if row[service + " Item"]
        }

    @property
    def currency_rate(self):
        """Return the current conversion rate for the countries currency to GBP."""
        if self._currency_rate is None:
            if self.currency_code is None or self.currency_code == "GBP":
                self._currency_rate = 1
            else:
                self._currency_rate = self.current_rate()
        return self._currency_rate

    @property
    def min_channel_fee(self):
        """Return minimum channel fee for country."""
        if self.currency_code is None:
            return 0
        return int((self.min_channel_fee_local * self.currency_rate) * 100)

    def __repr__(self):
        return self.name

    def __getitem__(self, key):
        return self.services[key]

    def get_exchange_rates(self):
        """Return the exchange rates for the country's currency."""
        URL = f"https://api.exchangerate-api.com/v4/latest/{self.currency_code}"
        response = requests.get(URL)
        response.raise_for_status()
        return response.json()["rates"]

    def current_rate(self):
        """Return current currency conversion rate to GBP."""
        if self.currency_code == "GBP":
            return 1
        rates = self.get_exchange_rates()
        return rates["GBP"]


class Service:
    """Container for international shipping services."""

    def __init__(self, item_price, kg_price):
        """
        Set item price and kilogram price.

        Arg:
            item_price: Price of shipping per item in GBP pence.
            kg_price: Price of shipping per kilogram in GBP pence.

        """
        self.item_price = int(item_price)
        self.kg_price = int(kg_price)

    def calculate_price(self, weight):
        """
        Return price to ship a single item.

        Args:
            weight: The weight of the item in kilograms.

        """
        return self.item_price + self.calculate_weight_price(weight)

    def calculate_weight_price(self, weight):
        """
        Return kilogram price for a given weight.

        Args:
            weight: The weight for which the price will be returned.

        """
        return int(weight / 1000 * self.kg_price)


countries = Countries()
