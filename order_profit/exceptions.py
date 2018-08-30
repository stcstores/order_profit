"""Exceptions for Order Profit."""


class ShippingRuleNotFound(Exception):
    """Base exception for errors in finding shipping rules for orders."""

    pass


class NoShippingRule(ShippingRuleNotFound):
    """Raised when no shipping rule can be found for an order."""

    text = "No shipping rules matching country_id {} and rule_id {}"

    def __init__(self, country_id, rule_id):
        """
        Raise exception.

        Args:
            country_id: ID of the country for which the shipping rule cannot
                be found.
            rule_id: The ID of the shipping rule applied to the order.
        """
        return super().__init__(self.text.format(country_id, rule_id))


class TooManyShippingRules(ShippingRuleNotFound):
    """Raised when multiple shipping rules are found for an order."""

    text = "Too many shipping rules ({}) found matching country_id {} and " "rule_id {}"

    def __init__(self, rules, country_id, rule_id):
        """
        Raise exception.

        Args:
            rules: Shipping ruls found for order.
            country_id: ID of the country for which the shipping rule cannot
                be found.
            rule_id: The ID of the shipping rule applied to the order.
        """
        return super().__init__(self.text.format(len(rules), country_id, rule_id))
