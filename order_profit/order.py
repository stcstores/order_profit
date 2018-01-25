from .product import Product


class Order:

    def __init__(self, update, dispatch_order):
        self.update = update
        self.order_id = dispatch_order.order_id
        self.dispatch_order = dispatch_order
        self.date_recieved = self.dispatch_order.date_recieved
        self.dispatch_date = self.dispatch_order.dispatch_date
        self.products = [
            Product(self.update, p) for p in dispatch_order.products]
        self.price = int(float(self.dispatch_order.total_gross_gbp) * 100)
        self.country_code = dispatch_order.delivery_country_code
        self.country = self.update.countries[self.country_code]
        self.weight = sum([p.weight * p.quantity for p in self.products])
        self.item_count = sum([p.quantity for p in self.products])
        self.vat_rate = self.calculate_vat()
        self.purchase_price = sum(
            [p.purchase_price * p.quantity for p in self.products])
        self.courier = self.get_courier()
        self.postage_price = self.courier.calculate_price(self)
        self.channel_fee = int(float(self.price / 100) * 15)
        self.profit = self.price - sum([
            self.postage_price, self.purchase_price, self.channel_fee])
        if self.vat_rate is not None:
            self.vat = int((self.price / 100) * self.vat_rate)
            self.profit_vat = self.profit - self.vat
        else:
            self.vat = None
            self.profit_vat = None

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
                'No courier rule found with name {}.'.format(courier_name))
        return rule.id

    def get_courier(self):
        return self.update.shipping_rules.get_shipping_rule(
            self.country_code, self.get_courier_rule_id())
