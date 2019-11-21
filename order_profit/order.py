"""The Order class."""

import logging

from .countries import countries
from .product import Product

logger = logging.getLogger("order_profit")


class Order:
    """
    Information about a Cloud Commerce Order with Profit Loss data.

    Attributes:
        update: order_pofit.OrderProfit creating the product.
        dispatch_order: Order data from CCAPI.
        order_id: The ID of the order.
        customer_id: The ID order customer.
        date_recieved: The date on which the order was recieved.
        dispatch_date: The date on which the order was dispatched.
        products: List of order_profit.product.Product objects containing the
            products ordered.
        price: The price of the order in GBP pence.
        country_code: The ID of the country to which the order was sent.
        county: Information about the country to which the order was sent
            as an order_profit.countries.Country object.
        department: The department to which the ordered product belong.
        weight: The total weight of the order in grams.
        item_count: The total number of items ordered.
        vat_rate: The rate of VAT charged on the order.
        purchase_price: The cost of the purchased items.
        courier: The shipping service used to send the order.
        postage_price: The cost to send the order.
        channel_fee: The fee charged by the selling channel.
        profit: The profit made on the order before VAT.
        vat: The VAT charged on the order.
        profit_vat: The profit made on the order after VAT.

    """

    def __init__(self, update, dispatch_order):
        """
        Load order data.

        Args:
            update: order_pofit.OrderProfit creating the product.
            dispatch_order: Order data from CCAPI.

        """
        self.update = update
        self.dispatch_order = dispatch_order
        self.order_id = int(self.dispatch_order.order_id)
        self.customer_id = int(self.dispatch_order.customer_id)
        self.date_recieved = self.dispatch_order.date_recieved
        self.dispatch_date = self.dispatch_order.dispatch_date
        self.country_code = dispatch_order.delivery_country_code
        self.country = countries[self.country_code]
        self.price = int(float(self.dispatch_order.total_gross_gbp) * 100)
        self.purchase_price = None
        self.courier = None
        self.item_count = None
        self.postage_price = None
        self.products = []
        self.error = False
        self.department = ""
        self.weight = 0
        self.item_count = 0
        self.vat_rate = 0
        self.purchase_price = 0
        self.channel_fee = 0
        self.profit = 0
        self.vat = 0
        self.profit_vat = 0
        try:
            self.process()
        except Exception as e:
            logger.exception(e)
            self.error = True

    def process(self):
        """Process the details of the order."""
        for product in self.dispatch_order.products:
            self.products.append(Product(self.update, product))
        self.department = self.get_department()
        self.weight = sum([p.weight * p.quantity for p in self.products])
        self.item_count = sum([p.quantity for p in self.products])
        self.vat_rate = self.calculate_vat()
        self.purchase_price = sum(
            [p.purchase_price * p.quantity for p in self.products]
        )
        self.courier = self.get_courier()
        self.postage_price = self.courier.calculate_price(self)
        self.channel_fee = self.get_channel_fee()
        self.profit = self.get_profit(self.price, self.purchase_price, self.channel_fee)
        if self.vat_rate is not None:
            self.vat = int((self.price / 100) * self.vat_rate)
            self.profit_vat = self.get_profit_vat(self.profit, self.vat)
        else:
            self.vat = None
            self.profit_vat = None

    def to_dict(self):
        """Return dict of product data."""
        return [p.to_dict() for p in self.products]

    def get_channel_fee(self):
        """Return channel fee charged on the order."""
        fee = int(float(self.price / 100) * 15)
        if fee < self.country.min_channel_fee:
            return self.country.min_channel_fee
        return fee

    def get_profit(self, price, purchase_price, channel_fee):
        """Return the profit made on the order before VAT."""
        if self.courier.is_valid_service is True:
            return price - sum(
                [self.postage_price, self.purchase_price, self.channel_fee]
            )
        else:
            return 0

    def get_profit_vat(self, profit, vat):
        """Return the profit made on the order after VAT."""
        if self.courier.is_valid_service is True:
            return profit - vat
        else:
            return 0

    def calculate_vat(self):
        """Return VAT charged on the order, if calculable."""
        if self.country.region == self.country.REST_OF_WORLD:
            return 0
        if len(self.products) == 1:
            return self.products[0].vat_rate
        order_vat_rates = list(set([p.vat_rate for p in self.products]))
        if len(order_vat_rates) == 1:
            return order_vat_rates[0]
        return None

    def get_courier_rule_id(self):
        """Return the Shipping Rule ID used for the order."""
        courier_name = self.dispatch_order.default_cs_rule_name.split(" - ")[0]
        try:
            rule = [r for r in self.update.courier_rules if r.name == courier_name][0]
        except IndexError:
            raise Exception(
                "No courier rule found with name {} for order {}.".format(
                    courier_name, self.order_id
                )
            )
        return rule.id

    def get_courier(self):
        """Return the shipping rule used by the order."""
        return self.update.shipping_rules.get_shipping_rule(
            self.country_code, self.get_courier_rule_id()
        )

    def get_department(self):
        """Return the department to which the ordered products belong."""
        departments = list(set([p.department for p in self.products]))
        if len(departments) == 1:
            return departments[0]
        return "Mixed"
