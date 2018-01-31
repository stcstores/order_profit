import time

from ccapi import CCAPI


class Product:

    def __init__(self, update, order_product):
        self.update = update
        self.order_product = order_product
        self.quantity = self.order_product.quantity
        self.inventory_product = self.get_product()
        self.weight = self.order_product.per_item_weight
        self.purchase_price = self.calculate_purchase_price()
        self.department = self.inventory_product.options[
            'Department'].value.value
        self.vat_rate = self.get_vat_rate()

    def get_vat_rate(self):
        if self.inventory_product.vat_rate in ('Vat Exempt', 'Zero Rated'):
            return 0
        return int(self.inventory_product.vat_rate.replace('%', ''))

    def get_product(self):
        if self.order_product.product_id in self.update.products:
            return self.update.products[self.order_product.product_id]
        for attempt in range(100):
            try:
                return CCAPI.get_product(self.order_product.product_id)
            except Exception:
                time.sleep(10)
                continue
            else:
                break
        else:
            raise Exception('Unable to load product {}.'.format(
                self.order_product.sku))

    def calculate_purchase_price(self):
        purchase_price = 0
        for attempt in range(100):
            try:
                purchase_price += int(float(
                    self.inventory_product.options[
                        'Purchase Price'].value.value) * 100)
            except Exception:
                continue
            else:
                break
        else:
            raise Exception(
                'Cannot load purchase price for product {}'.format(
                    self.sku))
        return purchase_price
