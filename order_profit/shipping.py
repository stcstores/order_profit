from . import exceptions
from .countries import Countries


class ShippingRule:

    countries = Countries()
    item_price = None
    kg_price = None
    name = None
    countries = []
    rule_ids = []
    EU_country_ids = [c.id for c in countries if c.region == 'EU']
    ROW_country_ids = [c.id for c in countries if c.region == 'ROW']

    def __repr__(self):
        return self.name

    @classmethod
    def calculate_price(cls, order_weight):
        if cls.item_price is None and cls.kg_price is None:
            return None
        if cls.kg_price is None:
            return cls.item_price
        return cls.calculate_kg_price(order_weight) + cls.item_price

    @classmethod
    def calculate_kg_price(cls, order_weight):
        return int(order_weight / 1000 * cls.kg_price)


class RoyalMail(ShippingRule):
    countries = [1, 14, 88, 103, 119]

    def matches(self, country_id, rule_id):
        return (int(rule_id) in self.rule_ids and
                int(country_id) in self.countries)

    def calculate_price(self, order):
        return self.item_price


class Spring(ShippingRule):
    countries = [1]

    @classmethod
    def matches(cls, country_id, rule_id):
        return (int(rule_id) in cls.rule_ids and int(country_id)
                not in cls.countries)

    @classmethod
    def calculate_price(cls, order):
        return order.country.services[cls.service].calculate_price(
            order.weight)


class Courier(ShippingRule):

    @classmethod
    def matches(cls, country_id, rule_id):
        return rule_id in cls.rule_ids


class RoyalMailUntracked48(RoyalMail):
    name = 'Royal Mail Untracked 48 Packet'
    item_price = 215
    rule_ids = [9584, 10580]


class RoyalMailUntracked24(RoyalMail):
    name = 'Royal Mail Untracked 48'
    item_price = 278
    rule_ids = [9583]


class RoyalMailTracked48Packet(RoyalMail):
    name = 'Royal Mail Tracked 48 Packet'
    item_price = 312
    rule_ids = [9586]


class RoyalMailTracked24Packet(RoyalMail):
    name = 'Royal Mail Tracked 24 Packet'
    item_price = 517
    rule_ids = [9585]


class RoyalMail48LargeLetter(RoyalMail):
    name = 'Royal Mail 48 Large Letter'
    item_price = 65
    rule_ids = [9588, 10579]


class RoyalMail24LargeLetter(RoyalMail):
    name = 'Royal Mail 24 Large Letter'
    item_price = 113
    rule_ids = [9587]


class RoyalMailHeavyAndLarge48(RoyalMail):
    name = 'Royal Mail Heavy and Large 48'
    item_price = 312
    rule_ids = [9814]


class RoyalMailHeavyAndLarge24(RoyalMail):
    name = 'Royal Mail Heavy and Large 24'
    item_price = 517
    rule_ids = [10114]


class SpringPAK(Spring):
    name = 'Spring Untracked (PAK)'
    service = 'PAK'
    rule_ids = [11747, 13771]


class SpringPAR(Spring):
    name = 'Spring Parcel (PAR)'
    service = 'PAR'
    rule_ids = [13764, 13769, 13992]


class SpringPAT(Spring):
    name = 'Spring Tracked (PAT)'
    service = 'PAT'
    rule_ids = [13451]


class SpringPAP(Spring):
    name = 'Spring Signed (PAP)'
    service = 'PAP'
    rule_ids = [13768, 13936]


class UKCourier(Courier):
    name = 'UK Courier'
    item_price = 630  # CHECK
    rule_ids = [11422]


class EUCourier(Courier):
    name = 'EU Courier'
    item_price = 1800
    countries = Courier.EU_country_ids
    rule_ids = [11243, 11245]


class ROWCourier(Courier):
    name = 'ROW Courier'
    item_price = 2200
    countries = Courier.ROW_country_ids
    rule_ids = [10284, 10390]


def all_subclasses(cls):
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)]


class ShippingRules:

    def __init__(self):
        self.shipping_rules = [
            cls() for cls in all_subclasses(ShippingRule) if
            len(cls.__subclasses__()) == 0]

    def get_shipping_rules(self, country_id, rule_id):
        return [
            r for r in self.shipping_rules if r.matches(country_id, rule_id)]

    def get_shipping_rule(self, country_id, rule_id):
        rules = self.get_shipping_rules(country_id, rule_id)
        if len(rules) == 1:
            return rules[0]
        if len(rules) == 0:
            raise exceptions.NoShippingRule(country_id, rule_id)
        raise exceptions.TooManyShippingRules(rules, country_id, rule_id)
