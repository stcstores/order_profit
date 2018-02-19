import json

from .product import Product


class Order:

    def __init__(self, update, dispatch_order):
        self.update = update
        self.dispatch_order = dispatch_order
        self.order_id = int(self.dispatch_order.order_id)
        self.customer_id = int(self.dispatch_order.customer_id)
        self.date_recieved = self.dispatch_order.date_recieved
        self.dispatch_date = self.dispatch_order.dispatch_date
        self.products = []
        for product in dispatch_order.products:
            try:
                self.products.append(Product(self.update, product))
            except Exception as e:
                print('Error with product {}.'.format(product.sku))
                raise e
        self.price = int(float(self.dispatch_order.total_gross_gbp) * 100)
        self.country_code = dispatch_order.delivery_country_code
        self.country = self.update.countries[self.country_code]
        self.department = self.get_department()
        self.weight = sum([p.weight * p.quantity for p in self.products])
        self.item_count = sum([p.quantity for p in self.products])
        self.vat_rate = self.calculate_vat()
        self.purchase_price = sum(
            [p.purchase_price * p.quantity for p in self.products])
        self.courier = self.get_courier()
        self.postage_price = self.courier.calculate_price(self)
        self.channel_fee = self.get_channel_fee()
        self.profit = self.price - sum([
            self.postage_price, self.purchase_price, self.channel_fee])
        if self.vat_rate is not None:
            self.vat = int((self.price / 100) * self.vat_rate)
            self.profit_vat = self.profit - self.vat
        else:
            self.vat = None
            self.profit_vat = None

    def serialize_products(self):
        return json.dumps([p.to_dict() for p in self.products])

    def get_channel_fee(self):
        fee = int(float(self.price / 100) * 15)
        if fee < self.country.min_channel_fee:
            return self.country.min_channel_fee
        return fee

    def calculate_vat(self):
        if self.country.region == self.country.REST_OF_WORLD:
            return 0
        if len(self.products) == 1:
            return self.products[0].vat_rate
        order_vat_rates = list(set([p.vat_rate for p in self.products]))
        if len(order_vat_rates) == 1:
            return order_vat_rates[0]
        return None

    def get_courier_rule_id(self):
        courier_name = self.dispatch_order.default_cs_rule_name.split(' - ')[0]
        try:
            rule = [
                r for r in self.update.courier_rules if
                r.name == courier_name][0]
        except IndexError:
            raise Exception(
                'No courier rule found with name {} for order {}.'.format(
                    courier_name, self.order_id))
        return rule.id

    def get_courier(self):
        return self.update.shipping_rules.get_shipping_rule(
            self.country_code, self.get_courier_rule_id())

    def get_department(self):
        departments = list(set([p.department for p in self.products]))
        if len(departments) == 1:
            return departments[0]
        return 'Mixed: {}'.format(', '.join(departments))
