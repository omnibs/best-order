from collections import defaultdict


class Context:
    def __init__(self, prices, qtys, minorder_shipping):
        self.prices_orig = prices
        # sellercount = len(prices[0])
        # convention: product ID is its index in the array
        #               seller ID is its index in the array + 100
        #                 (to be easy to spot if we mix them up)
        self.products = [Product(i, x) for i, x in enumerate(qtys)]
        self.sellers = [Seller(100+i, minorder, shipping)
                        for i, (minorder, shipping)
                        in enumerate(minorder_shipping)]

        self.prices = [Context.create_prices(i, product_prices) for i, product_prices in enumerate(prices)]
        self.prices = sum(self.prices, [])  # flattening the list

        # index for quickly accessing seller info
        self.seller_idx = defaultdict(None)
        for s in self.sellers: self.seller_idx[s.id] = s
        self.product_idx = defaultdict(None)
        for p in self.products: self.product_idx[p.id] = p

    @staticmethod
    def create_prices(product_id, prices):
        return [Price(100+i,product_id,price)
                for i, price
                in enumerate(prices)
                if price is not None]

class Product:
    def __init__(self, id, qty):
        self.id = id
        self.qty = qty

class Price:
    def __init__(self, seller_id, product_id, price):
        self.seller_id = seller_id
        self.product_id = product_id
        self.price = price

class Seller:
    def __init__(self, id, minorder, shipping):
        self.id=id
        self.minorder=minorder
        self.shipping=shipping

class Order:
    # the calculates the product cost, shipping cost and total cost
    def __init__(self, ctx, prices):
        sellers = defaultdict(None)
        for p in prices:
            sellers[p.seller_id] = 1
        self.shipping_prices = [ctx.seller_idx[k].shipping for k in sellers]
        self.shipping_total = sum(self.shipping_prices)
        self.product_total = sum(Order.product_price(ctx, p) for p in prices)
        self.total = self.shipping_total + self.product_total
        self.prices_paid = prices
        self.sellers = sellers

    # checks an order is valid
    @staticmethod
    def check_order(ctx, prices):
        return Order.above_min_order(ctx, prices)

    # checks an order is above minimum order value
    @staticmethod
    def above_min_order(ctx, prices):
        value_by_seller = defaultdict(int)
        for price in prices:
            value_by_seller[price.seller_id] += Order.product_price(ctx, price)

        return all(ctx.seller_idx[k].minorder <= value_by_seller[k] for k in value_by_seller)

    @staticmethod
    def product_price(ctx, p):
        return p.price * ctx.product_idx[p.product_id].qty

class BruceForce:
    def __init__(self, ctx):
        self._ctx = ctx
        self._lowestPrice = -1
        self._lowestPriceOrder = []

        # index prices by product id so it's easier to access them
        self._prices = defaultdict(list)
        for p in ctx.prices: self._prices[p.product_id].append(p)

    def create_order(self):
        self.crunch([])
        return self._lowestPriceOrder

    # crunch is a recursive function
    # order is our list of selected prices, one for each product in the cart
    # crunch creates all possible permutations, storing the cheapest found along the way
    def crunch(self, order):
        idx = len(order)
        pid = self._ctx.products[idx].id
        if (self._prices[pid] == None):
            return
        for price in self._prices[pid]:
            if price is None: continue
            # create a copy of the current order and add this price to it
            new_order = order[:]
            new_order.extend([price])
            # if we have a full order (all products), save it if it's the cheapest seen
            # otherwise, keep building permutation
            if (len(new_order) == len(self._ctx.products)):
                self.save_if_lowest_price(new_order)
            else:
                self.crunch(new_order)

    def save_if_lowest_price(self, order):
        if (not Order.check_order(self._ctx, order)):
            return
        order = Order(self._ctx, order)
        if (self._lowestPrice == -1 or self._lowestPrice > order.total):
            self._lowestPrice = order.total
            self._lowestPriceOrder = order
