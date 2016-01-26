from product import Stock
from datetime import datetime
import time 

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
	log = open('/home/xinx/Hsino/data/collect.log','a')
	update_time = str(datetime.now())[:19]
	info = 'The database is updated at {}\n'.format(update_time)
	log.write(info)
	log.close()

def main():
	while True:
		update(1)
		time.sleep(7200)

if __name__ == '__main__':
	main()
