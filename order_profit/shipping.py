"""Shipping rules used to send orders."""

from . import exceptions


class ShippingRule:
    """Base class for shipping rules.

    Attributes:
        item_price: The price of shipping per item in GBP pence.
        kg_price: The price of shipping per kilogram in GBP pence.
        name: The name of the shipping rule.
        countries: List of country IDs of countries to which this shipping rule
            can be used.
        rule_ids: List of Cloud Commerce Shipping Rule IDs which match this
            shipping rule.

    """

    item_price = None
    kg_price = None
    name = None
    countries = []
    rule_ids = []
    EU_country_ids = [c.id for c in countries if c.region == "EU"]
    ROW_country_ids = [c.id for c in countries if c.region == "ROW"]
    is_valid_service = True

    def __repr__(self):
        return self.name

    @classmethod
    def calculate_price(cls, order_weight):
        """
        Return cost to ship an order.

        Args:
            order_weight: The total weight of the order in grams.

        """
        if cls.item_price is None and cls.kg_price is None:
            return None
        if cls.kg_price is None:
            return cls.item_price
        return cls.calculate_kg_price(order_weight) + cls.item_price

    @classmethod
    def calculate_kg_price(cls, order_weight):
        """
        Return kilogram cost to ship an order.

        Args:
            order_weight: The total weight of the order in grams.

        """
        return int(order_weight / 1000 * cls.kg_price)


class ErrorShippingRule(ShippingRule):
    """Shipping rule for orders sent with the error shipping rule."""

    rule_ids = [10008]
    name = "Error"
    is_valid_service = False

    @classmethod
    def matches(cls, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return rule_id in cls.rule_ids

    @classmethod
    def calculate_price(self, order):
        """No price can be provided as this is an invalid shipping rule."""
        return 0


class SecuredMailRoyalMail(ShippingRule):
    """Base rule for UK orders sent through Secured Mail and Royal Mail."""

    @classmethod
    def calculate_price(cls, order):
        """
        Return cost to ship an order.

        Args:
            order_weight: The total weight of the order in grams.

        """
        return cls.item_price

    @classmethod
    def matches(cls, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return rule_id in cls.rule_ids


class SecuredMailInternational(ShippingRule):
    """Base shipping rule for Secured Mail international post."""

    @classmethod
    def calculate_price(cls, order):
        """
        Return cost to ship an order.

        Args:
            order_weight: The total weight of the order in grams.

        """
        return order.country.services[cls.service].calculate_price(order.weight)

    @classmethod
    def matches(cls, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return rule_id in cls.rule_ids


class SecuredMailInternationalUntracked(SecuredMailInternational):
    """Shipping rule for Secured Mail International Untracked."""

    name = "Secured Mail International Untracked"
    service = "SMIU"
    item_price = 9999
    rule_ids = [16416, 16417]


class SecuredMailInternationalTracked(SecuredMailInternational):
    """Shipping rule for Secured Mail International Tracked."""

    name = "Secured Mail International Tracked"
    service = "SMIT"
    rule_ids = [16419]


class RoyalMail(ShippingRule):
    """Base shipping rule for Royal Mail shipping services."""

    countries = [1, 14, 88, 103, 119]

    def matches(self, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return int(rule_id) in self.rule_ids and int(country_id) in self.countries

    def calculate_price(self, order):
        """
        Return cost to ship an order.

        Args:
            order_weight: The total weight of the order in grams.

        """
        return self.item_price


class Spring(ShippingRule):
    """Base shipping rule for Spring shipping services."""

    countries = [1]

    @classmethod
    def matches(cls, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return int(rule_id) in cls.rule_ids and int(country_id) not in cls.countries

    @classmethod
    def calculate_price(cls, order):
        """
        Return cost to ship an order.

        Args:
            order_weight: The total weight of the order in grams.

        """
        return order.country.services[cls.service].calculate_price(order.weight)


class Courier(ShippingRule):
    """Base shipping rule for Courier shipping services."""

    @classmethod
    def matches(cls, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return rule_id in cls.rule_ids


class Prime(ShippingRule):
    """Base shipping rule for Amazon Prime shipping services."""

    name = "Prime"
    rule_ids = [15401, 15402, 15403, 15434, 15435, 15436]
    countries = [1]
    item_price = 312

    @classmethod
    def matches(cls, country_id, rule_id):
        """
        Return True if this shipping rule is applicable.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return rule_id in cls.rule_ids


class SecuredMailRoyalMailPacket(SecuredMailRoyalMail):
    """Shipping rule for Royal Mail packets sent throgh Secured Mail."""

    name = "Secured Mail Royal Mail Packet"
    rule_ids = [18777]
    item_price = 175


class SecuredMailRoyalMailLargeLetter(SecuredMailRoyalMail):
    """Shipping rule for Royal Mail large letters sent throgh Secured Mail."""

    name = "Secured Mail Royal Mail Large Letter"
    rule_ids = [18779, 18780]
    item_price = 60


class Prime48(Prime):
    """Shipping rule for Amazon Prime 48 hour shipping service."""

    name = "Prime 48"
    rule_ids = [15436]
    countries = [1]
    item_price = 312


class Prime24(Prime):
    """Shipping rule for Amazon Prime 24 hour shipping service."""

    name = "Prime 24"
    rule_ids = [15434, 15435]
    countries = [1]
    item_price = 550


class RoyalMailUntracked48(RoyalMail):
    """Shipping rule for Royal Mail Untracked 48 shipping service."""

    name = "Royal Mail Untracked 48 Packet"
    item_price = 215
    rule_ids = [9584, 18781]


class RoyalMailUntracked24(RoyalMail):
    """Shipping rule for Royal Mail Untracked 24 shipping service."""

    name = "Royal Mail Untracked 28"
    item_price = 278
    rule_ids = [9583]


class RoyalMailTracked48Packet(RoyalMail):
    """Shipping rule for Royal Mail Tracked 48 shipping service."""

    name = "Royal Mail Tracked 48 Packet"
    item_price = 397
    rule_ids = [9586]


class RoyalMailTracked24Packet(RoyalMail):
    """Shipping rule for Royal Mail Tracked 24 shipping service."""

    name = "Royal Mail Tracked 24 Packet"
    item_price = 517
    rule_ids = [9585, 10580]


class RoyalMail48LargeLetter(RoyalMail):
    """Shipping rule for Royal Mail Large Letter 48 shipping service."""

    name = "Royal Mail 48 Large Letter"
    item_price = 65
    rule_ids = [9588, 18780]


class RoyalMail24LargeLetter(RoyalMail):
    """Shipping rule for Royal Mail Large Letter 24 shipping service."""

    name = "Royal Mail 24 Large Letter"
    item_price = 113
    rule_ids = [9587, 10579]


class RoyalMailHeavyAndLarge48(RoyalMail):
    """Shipping rule for Royal Mail Heavy and Large 48 shipping service."""

    name = "Royal Mail Heavy and Large 48"
    item_price = 399
    rule_ids = [9814]


class RoyalMailHeavyAndLarge24(RoyalMail):
    """Shipping rule for Royal Mail Heavy and Large 24 shipping service."""

    name = "Royal Mail Heavy and Large 24"
    item_price = 517
    rule_ids = [10114]


class SpringPAK(Spring):
    """Shipping rule for Spring Untracked International."""

    name = "Spring Untracked (PAK)"
    service = "PAK"
    rule_ids = [11747, 13771]


class SpringPAR(Spring):
    """Shipping rule for Spring Parcel International."""

    name = "Spring Parcel (PAR)"
    service = "PAR"
    rule_ids = [13764, 13769, 13992]


class SpringPAT(Spring):
    """Shipping rule for Spring Tracked International."""

    name = "Spring Tracked (PAT)"
    service = "PAT"
    rule_ids = [13451]


class SpringPAP(Spring):
    """Shipping rule for Spring Signed International."""

    name = "Spring Signed (PAP)"
    service = "PAP"
    rule_ids = [13768, 13936]


class UKCourier(Courier):
    """Shipping rule for UK couriers."""

    name = "UK Courier"
    item_price = 700
    rule_ids = [11422]


class EUCourier(Courier):
    """Shipping rule for EU couriers."""

    name = "EU Courier"
    item_price = 1800
    countries = Courier.EU_country_ids
    rule_ids = [11243, 11245, 16886]


class ROWCourier(Courier):
    """Shipping rule for non EU couriers."""

    name = "ROW Courier"
    item_price = 2200
    countries = Courier.ROW_country_ids
    rule_ids = [10284, 10390]


def all_subclasses(cls):
    """Return recursive list of all subclasses of cls."""
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)
    ]


class ShippingRules:
    """Container for shipping rules."""

    def __init__(self):
        """Load shipping rules."""
        self.shipping_rules = [
            cls()
            for cls in all_subclasses(ShippingRule)
            if len(cls.__subclasses__()) == 0
        ]

    def get_shipping_rules(self, country_id, rule_id):
        """
        Return list of applicable shipping rules or an order.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        """
        return [r for r in self.shipping_rules if r.matches(country_id, rule_id)]

    def get_shipping_rule(self, country_id, rule_id):
        """
        Return shipping rule for order.

        Args:
            country_id: The country ID to which the order was sent.
            rule_id: The shipping rule applied to the order.

        Returns:
            order_profit.shipping.ShippingRule

        Raises:
            order_profit.exceptions.NoShippingRule: If no applicable shipping
                service is found.
            order_profit.exceptions.TooManyShippingRules: If more than one
                applicable shipping service is found.

        """
        rules = self.get_shipping_rules(country_id, rule_id)
        if len(rules) == 1:
            return rules[0]
        if len(rules) == 0:
            raise exceptions.NoShippingRule(country_id, rule_id)
        raise exceptions.TooManyShippingRules(rules, country_id, rule_id)
