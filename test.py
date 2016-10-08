import unittest
from order import Product, Context, BruceForce
from solution_joe import LinOpt

class TestBestOrder(unittest.TestCase):

	def test_i_know_python(self):
		p = Product(1, 2)
		self.assertEqual(p.id, 1)
		self.assertEqual(p.qty, 2)

	def test_create_scenario(self):
		prices = [
			[1,2,None], # product id=0 [$1 at seller 100, $2 at seller 102, not stocked at seller 103]
			[None,2,3]  # product id=1 [not stocked at seller 101, $2 at seller 102, $3 at seller 103]
		]
		qtys = [10,20] # [10 units of product 0, 20 units of product 1]
		seller = [
			(88,10), # seller id=100: minimum order $88, $10 shipping
			(1,10),  # seller id=102: minimum order $1, $10 shipping
			(10,10), # seller id=103: minimum order $10, $10 shipping
		]

		ctx = Context(prices, qtys, seller)

		self.assertEqual(len(ctx.products), 2)
		self.assertEqual(ctx.products[0].id, 0)
		self.assertEqual(ctx.products[0].qty, 10)
		self.assertEqual(ctx.sellers[0].id, 100)
		self.assertEqual(ctx.sellers[0].minorder, 88)
		self.assertEqual(ctx.sellers[0].shipping, 10)
		self.assertEqual(ctx.prices[0].product_id, 0)
		self.assertEqual(ctx.prices[0].seller_id, 100)
		self.assertEqual(ctx.prices[0].price, 1)

	# simplest scenario, 1 product 1 seller, all good
	def test_takes_orders(self):
		prices = [[10]]
		qtys = [4]
		seller = [(20,10)]
		ctx = Context(prices, qtys, seller)
		order = BruceForce(ctx).create_order()

		self.assertEqual(order.shipping_total, 10)
		self.assertEqual(order.total, 50)

	# one product, 3 sellers, clear winner
	def test_chooses_best_seller_straighforward(self):
		prices = [[20, 15, 10]]
		qtys = [4]
		seller = [
			(40,10),
			(30,10),
			(20,10)
		]
		ctx = Context(prices, qtys, seller)
		order = BruceForce(ctx).create_order()

		self.assertEqual(order.total, 50)

	def test_respects_minimum_order(self):
		prices = [[20, 15, 10]]
		qtys = [4]
		seller = [
			(40,10),
			(30,10),
			(200,10) # <<-- now cheapest price of 10 won't be valid
		]
		ctx = Context(prices, qtys, seller)
		order = BruceForce(ctx).create_order()

		self.assertEqual(order.total, 70)

	def test_considers_shipping(self):
		prices = [[20, 15, 10]]
		qtys = [4]
		seller = [
			(40,10),
			(30,20), # <<-- this one's the best
			(20,100) # <<-- shipping too expensive
		]
		ctx = Context(prices, qtys, seller)
		order = BruceForce(ctx).create_order()

		self.assertEqual(order.total, 80)

	# shipping at seller 1 is expensive
	# combined shipping of other sellers is more expensive tho
	def test_pricy_shipping_is_ok_versus_splitting_over_many_sellers(self):
		prices = [
			[10, 10, None, None],
			[10, None, 10, None],
			[10, None, None, 10]
		]
		qtys = [1,1,1]
		seller = [
			(10, 20), # <<-- pricier shipping, still cheaper than ordering from 3 sellers
			(10, 10),
			(10, 10),
			(10, 10)
		]

		ctx = Context(prices, qtys, seller)
		order = BruceForce(ctx).create_order()

		self.assertEqual(order.shipping_total, 20)
		self.assertEqual(order.total, 50)
		self.assertEqual(order.product_total, 30)

	# worst price is the only one that matches minimum order
	def test_minimum_order_not_obvious(self):
		prices = [
			[30, 10, None,   10],
			[30, 20,   10,   10],
			[30,  5,   10, None]
		]
		qtys = [1,1,1]
		seller = [
			(90, 50), # <<-- its a stab in the eye, but it's the only one that works
			(40, 10), # <<-- almost, we max out at $35
			(20, 10), # <<-- hit max, but doesn't have all products so no good
			(20, 10)  # <<-- same
		]

		ctx = Context(prices, qtys, seller)
		order = BruceForce(ctx).create_order()

		self.assertEqual(order.shipping_total, 50)
		self.assertEqual(order.total, 140)
		self.assertEqual(order.product_total, 90)

	def test_scipy(self):
		prices = [
			[30, 10,   10],
			[30, 20,   10],
			[30,  5,   10]
		]
		qtys = [3,3,3]
		seller = [
			(5, 50), # <<-- its a stab in the eye, but it's the only one that works
			(5, 10), # <<-- almost, we max out at $35
			(5, 10), # <<-- hit max, but doesn't have all products so no good
			(5, 10)  # <<-- same
		]

		ctx = Context(prices, qtys, seller)
		res = LinOpt(ctx).create_order()

		print(res)


	# def test_too_slow_for_bruteforce(self):
	# 	prices = [
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10],
	# 		[1002, 100, 50, 50],
	# 		[1001, 101, 10, 10]
	# 	]
	# 	qtys = [1, 2, 3, 1, 1, 2, 2, 3, 2, 1]
	# 	seller = [
	# 		(0,1),
	# 		(0,2),
	# 		(0,3),
	# 		(0,1)
	# 	]
	#
	# 	ctx = Context(prices, qtys, seller)
	# 	order = BruceForce(ctx).create_order()

if __name__ == '__main__':
	unittest.main()
