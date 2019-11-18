"""The Product class."""

import time

from ccapi import CCAPI


class Product:
    """
    Cloud Commerce Product with profit/loss data.

    Attributes:
        update: order_pofit.OrderProfit creating the product.
        order_product: Product data from the order.
        sku: The SKU of the product.
        quantity: The quantity of this product ordered.
        inventory_product: ccapi.inventory_items.Product for this product.
        weight: The weight of the product.
        purchase_price: The products Purchase Price in GBP pence.
        department: The department to which the product belongs.
        vat_rate: The VAT charged on the product in the UK.
        product_id: The ID of the product.
        range_id: The ID of the product's range.
        name: The full name of the product.

    """

    def __init__(self, update, order_product):
        """Cloud Commerce Product with profit/loss data.

        Args:
            update: order_pofit.OrderProfit creating the product.
            order_product: Product data from the order.

        """
        self.update = update
        self.order_product = order_product
        self.sku = self.order_product.sku
        self.quantity = self.order_product.quantity
        self.inventory_product = self.get_product()
        self.weight = self.order_product.per_item_weight
        self.purchase_price = self.calculate_purchase_price()
        self.department = self.inventory_product.options["Department"].value.value
        self.vat_rate = self.get_vat_rate()
        self.product_id = self.inventory_product.id
        self.range_id = self.inventory_product.range_id
        self.name = self.inventory_product.full_name

    def get_vat_rate(self):
        """Return the product's UK VAT rate."""
        try:
            return int(self.inventory_product.vat_rate)
        except Exception:
            raise Exception(f"Unable to retrive VAT rate for product {self.sku}.")

    def to_dict(self):
        """Return product info as a dict."""
        return {
            "sku": self.sku,
            "product_id": self.product_id,
            "range_id": self.range_id,
            "name": self.name,
            "quantity": self.quantity,
        }

    def get_product(self):
        """
        Return product inventory data from Cloud Commerce.

        Returns:
            ccapi.inventory_items.Product.

        """
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
            raise Exception("Unable to load product {}.".format(self.order_product.sku))

    def calculate_purchase_price(self):
        """Return the purchase price of the product."""
        purchase_price = 0
        for attempt in range(250):
            try:
                purchase_price += int(
                    float(self.inventory_product.options["Purchase Price"].value.value)
                    * 100
                )
            except Exception as e:
                print(e)
                continue
            else:
                break
        else:
            raise Exception(
                "Cannot load purchase price for product {}".format(self.sku)
            )
        return purchase_price
