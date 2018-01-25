class ShippingRuleNotFound(Exception):
    pass


class NoShippingRule(ShippingRuleNotFound):
    text = 'No shipping rules matching country_id {} and rule_id {}'

    def __init__(self, country_id, rule_id):
        return super().__init__(self.text.format(country_id, rule_id))


class TooManyShippingRules(ShippingRuleNotFound):
    text = ('Too many shipping rules ({}) found matching country_id {} and '
            'rule_id {}')

    def __init__(self, rules, country_id, rule_id):
        return super().__init__(
            self.text.format(len(rules), country_id, rule_id))
