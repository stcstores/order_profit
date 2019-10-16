"""
Order Profit.

Get Profit/Loss data from Cloud Commerce Pro.
"""
import logging

from .order_profit import OrderProfit

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["OrderProfit"]
