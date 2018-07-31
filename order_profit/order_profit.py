"""The Order Profit class."""

import sys

from ccapi import CCAPI

from .countries import Countries
from .order import Order
from .shipping import ShippingRules


class OrderProfit:
    """Retrive Profit/Loss data from Cloud Commerce Pro."""

    countries = Countries()
    number_of_days = 1

    def __init__(self):
        """Load Profit/Loss data from Cloud Commerce."""
        self.courier_rules = CCAPI.get_courier_rules()
        self.shipping_rules = ShippingRules()
        self.products = {}
        orders = self.filter_orders(self.get_orders())
        self.orders = self.process_orders(orders)
        self.orders.sort(key=lambda x: (x.profit_vat is None, x.profit_vat))

    def get_orders(self):
        """Return dispatched orders from Cloud Commerce."""
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=self.number_of_days)

    def filter_orders(self, orders):
        """Return filtered list of orders."""
        orders = [  # Filter resends
            order for order in orders if float(order.total_gross_gbp) > 0]
        return orders

    def process_orders(self, orders):
        """Return list of orders as order_profit.order.Order."""
        processed_orders = []
        for i, order in enumerate(orders):
            try:
                processed_orders.append(Order(self, order))
            except Exception as e:
                print('Error processing order {}.'.format(order.order_id))
                raise e
            percentage = int(((i + 1) / len(orders)) * 100)
            sys.stdout.write("\r{}%".format(percentage))
            sys.stdout.flush()
        sys.stdout.write('\r\n')
        sys.stdout.flush()
        return processed_orders