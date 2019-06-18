import numpy as np
import json

from typing import List


class CatalogProduct:
    """Product definition"""

    def __init__(self, product_code: int, std_price: float, npu_ratio: float, cost: float, cons_cost: float):
        self.product_code = product_code
        self.std_price = std_price
        self.npu_ratio = npu_ratio
        self.cost = cost
        self.cons_cost = cons_cost


class EvaluatedProduct:
    """Product evaluation for specific discount and v1

    discount - pass real number, not percent value (0.5 instead of 50%)
    """

    def __init__(self, product: CatalogProduct, discount: float, forecast: float):
        self.product = product
        self.discount = discount
        self.forecast = forecast

    @property
    def gross_price(self) -> float:
        """Return the gross price of the product (price - discount)"""
        return self.product.std_price * (1 - self.discount)

    @property
    def net_price(self) -> float:
        """Return the net price of the product ((price - discount) * NPU)"""
        return self.gross_price / self.product.npu_ratio

    @property
    def net_sales(self) -> float:
        """Return sales of the product (net price * v1)"""
        return self.net_price * self.forecast

    @property
    def cost_of_sales(self) -> float:
        """Return cost of sales for the product and v1 (cost * v1)"""
        return self.product.cost * self.forecast

    @property
    def cons_cost_of_sales(self) -> float:
        """Return consolidated cost of sales for the product and v1 (cons.cost * v1)"""
        return self.product.cons_cost * self.forecast


class EvaluatedCatalog:
    """Catalog evaluation for set of evaluated products"""

    def __init__(self, products: List[EvaluatedProduct], active_count: int):
        self.products = products
        self.active_count = active_count

        self.net_sales = np.sum([p.net_sales for p in self.products])
        self.cost_of_sales = np.sum([p.cost_of_sales for p in self.products])
        self.cons_cost_of_sales = np.sum([p.cons_cost_of_sales for p in self.products])

        self.profit = self.net_sales - self.cost_of_sales
        self.cons_profit = self.net_sales - self.cons_cost_of_sales
        self.gross_margin = 1 - (self.cost_of_sales / self.net_sales)
        self.cons_gross_margin = 1 - (self.cons_cost_of_sales / self.net_sales)

        self.upa = np.sum([p.forecast for p in self.products]) / self.active_count
        self.npu = self.net_sales / np.sum([p.forecast for p in self.products])
        self.spa = self.net_sales / self.active_count

    def to_dict(self):
        return {
            "active_count": self.active_count,
            "products_count": self.products.count(),
            "net_sales": self.net_sales,
            "cost_of_sales": self.cost_of_sales,
            "cons_cost_of_sales": self.cons_cost_of_sales,
            "profit": self.profit,
            "cons_profit": self.cons_profit,
            "gross_margin": self.gross_margin,
            "cons_gross_margin": self.cons_gross_margin,

            "upa": self.upa,
            "npu": self.npu,
            "spa": self.spa,
        }
