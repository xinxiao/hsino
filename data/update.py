from stock import Stock

PORTFOLIO = {
	    	'NYSE' : [],
		'NASDAQ' : ['MSFT', 'AAPL', 'FB',
			    'GOOGL'],
		'SHA' : []
	    }

def update(period):
	for exchange in PORTFOLIO:
		for ticker in PORTFOLIO[exchange]:
			stock = Stock(exchange, ticker)
			stock.store(period)

def main():
	update(15)

if __name__ == '__main__':
	main()
