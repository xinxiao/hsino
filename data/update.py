from stock import Stock

PORTFOLIO = {
	    	'SHA' : [],
                'HKG' : [],
                'TYO' : ['7203','7267','7201',
			 '6752','6758','9202',
			 '9201','9020','6501',
			 '6502','8058','8031',
			 '7751','7731'],
		'KRX' : ['005935','023530'],
		'SGX' : ['Z74','D05'],
		'NYSE' : ['BABA'],
		'NASDAQ' : ['MSFT','AAPL','FB',
			    'GOOGL','YHOO','TSLA',
			    'INTC','AMZN','CSCO'],
		'LON' : ['HSBA','BARC','VOD',
			 'RDSA','BP','LLOY'],
		'ETR' : ['SIE','BMW','VOW3']
	    }

def update(period):
	for exchange in PORTFOLIO:
		for ticker in PORTFOLIO[exchange]:
			stock = Stock(exchange, ticker)
			stock.store(period)
			print stock
			print ''

def main():
	update(15)

if __name__ == '__main__':
	main()
