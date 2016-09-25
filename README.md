# Marketplace order placement problem

## The Scenario

### A Marketplace

Imagine you're a marketplace website, people come in, make bulk orders of around 50 products, and every order can be fulfulled by an average of 2000 sellers. Customers don't care who's fulfilling their orders, they just care how much they pay. Your goal is to create for them the best possible order, splitting products between sellers according to price and shipping rates.

![shitty drawing of the process]()

### Orders

In this scenario what matters to us is just the products and the amounts.

One interesting thing about this business, that might matter for coming up with a good solution, is that among the products in the shopping cart, a large part of the paid price is concentrated in few products that are purchased in larger amounts.

![pie chart of price distribution]()

### Sellers

Each seller has a minimum order value, you can't order a $3 toothbrush from them, even if they have the best price.

Not all sellers stock all products, and for simplicity I've made that binary on the API. They can either stock infinite amounts or not sell the product at all.

Sellers also charge for the shipping. For convenience whatever prices are given on the API are prices already calculated for that specific order. For simplicity I've made them fixed price, you pay the same rate whether you buy 50 pounds of cheese or a ton.

So some interesting scenarios might come up here:

* Seller has expensive shipping rate and prices are not that good, but it's stock covers most of our shopping cart. He might be the cheapest, compared to splitting the order up into many different sellers and paying multiple shipping rates.
* Seller has awesome price for some products but crappy shipping rate, hard to know whether he's a good choice.

A hard problem that could be considered here, but wasn't, is when splitting up the quantities for a given product might result in a cheaper order. I've not considered this because it would increase complexity a lot, I believe.

## What's this?

This is a scenario I hit at work once, it seems like a hard problem and I solved it in the best possible way I could in 3 days with no heavy algorithms background to help me. I don't even know what "kind" of algorithm is required to solve this.

I built this simplified version of it because I wanted to discuss with people how to solve it. The original problem dealt with different price tiers for different quantities (50 shirts are cheaper per unit than 10), payment condition discounts (card's more expensive than cash on delivery), and shipping discounts depending on order size (very big orders pay no shipping), so complexity was waaay worse. 

I'm not 100% sure the best algorithm for this simplified scenario would be good for the real one, but we'll find out.

## Structure

The repo is comprised of a test suite validating the rules that implementations must obey and a simple performance with 16 products on 4 sellers. The suite runs against a bruteforce implementation in python which performs horribly.

The scenarios are specified in a very succint way, for example:

### Example scenario: two products, three sellers

In this scenario we're buying:

* 10 units of Product 1
* 20 units of Product 2

We have 3 sellers able to fulfill the order:

* Seller 1 stock Product 1 at $1
* Seller 2 stocks Product 1 at $2 and Product 2 at $2
* Seller 3 stocks Product 2 at $3

Sellers have the following minimum orders and shipping rates:

* Seller 1 has a minimum order of $88 and charges $10 for shipping
* Seller 2 has a minimum order of $1 and charges $10 for shipping
* Seller 3 has a minimum order of $10 and charges $10 for shipping

Here's how it looks in code:

```python
	def test_create_scenario(self):
		prices = [
			[1,2,None], # product 1 [$1 at seller 1, $2 at seller 2, not stocked at seller 3]
			[None,2,3]  # product 2 [not stocked at seller 1, $2 at seller 2, $3 at seller 3]
		]
		qtys = [10,20] # [qty for product 1, qty for product 2]
		seller = [
			(88,10), # seller 1: minimum order $88, $10 shipping
			(1,10),
			(10,10),
		]

		ctx = Context(prices, qtys, seller)
```

Product IDs and Seller IDs are derived from their indexes on the arrays. Product IDs start at 0, Seller IDs start at 100, just so it's obvious when we're mixing them up.

Context holds all the information an algorithm will need to crunch through this.

## How do I solve it?

The goal is to make something fast, that works for 50 products and 2000 sellers in under 3 secs on a developer laptop, and that still passes the tests.
