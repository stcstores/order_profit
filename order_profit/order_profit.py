"""The Order Profit class."""

import sys

from ccapi import CCAPI

from .countries import Countries
from .order import Order
from .shipping import ShippingRules


class OrderProfit:
    """Retrive Profit/Loss data from Cloud Commerce Pro."""

    number_of_days = 1

    def __init__(self):
        """Load Profit/Loss data from Cloud Commerce."""
        self.countries = Countries()
        self.courier_rules = CCAPI.get_courier_rules()
        self.shipping_rules = ShippingRules()
        self.products = {}
        orders = self.filter_orders(self.get_orders())
        self.orders = self.process_orders(orders)

    def get_orders(self):
        """Return dispatched orders from Cloud Commerce."""
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=self.number_of_days
        )

    def filter_orders(self, orders):
        """Return filtered list of orders."""
        orders = [  # Filter resends
            order for order in orders if float(order.total_gross_gbp) > 0
        ]
        return orders

    def process_orders(self, orders):
        """Return list of orders as order_profit.order.Order."""
        processed_orders = []
        for i, order in enumerate(orders):
            order = Order(self, order)
            processed_orders.append(order)
            print(
                f"Processing order {order.order_id} ({i + 1} of {len(orders)})",
                file=sys.stderr,
            )
        return processed_orders
