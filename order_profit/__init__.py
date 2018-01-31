from ccapi import CCAPI
from .countries import Countries
from . shipping import ShippingRules
from .order import Order


class OrderProfit:

    countries = Countries()
    number_of_days = 1

    def __init__(self):
        self.courier_rules = CCAPI.get_courier_rules()
        self.shipping_rules = ShippingRules()
        self.products = {}
        orders = self.filter_orders(self.get_orders())
        self.orders = self.process_orders(orders)
        self.orders.sort(key=lambda x: (x.profit_vat is None, x.profit_vat))

    def get_orders(self):
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=self.number_of_days)

    def filter_orders(self, orders):
        orders = [  # Filter resends
            order for order in orders if float(order.total_gross_gbp) > 0]
        return orders

    def process_orders(self, orders):
        processed_orders = []
        for i, order in enumerate(orders):
            processed_orders.append(Order(self, order))
            print('Processing order {} of {}'.format(i + 1, len(orders)))
        return processed_orders
