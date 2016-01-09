from stock import Stock

class Portfolio:

	def __init__(self):
		self.stock = []	
	
	def info():
		
	
	def add_stock(self, stock):
		if type(stock) == list:
			self.stock += stock
			return True
		else if isinstance(stock, Stock):
			self.stock += [stock]
			return True
		return False

	def collect(period):
		for stock in self.stock:
			stock.store(period)
