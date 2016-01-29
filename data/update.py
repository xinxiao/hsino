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
	start_time = datetime.now()

	for exchange in PORTFOLIO:
		for ticker in PORTFOLIO[exchange]:
			stock = Stock(exchange, ticker)
			stock.store(period)

	finished_time = datetime.now()
	
	log = open('/home/xinx/Hsino/data/collect.log','a')
	update_log = 'Database update - start:{}  end:{} \n'
	update_log = update_log.format(str(start_time)[:19],
				       str(finished_time)[:19])
	log.write(update_log)
	log.close()

	time_taken = (finished_time - start_time).seconds
	return time_taken

def main():
	while True:
		time_taken = update(1)
		sleep_time = 3600 - time_taken
		time.sleep(sleep_time)

if __name__ == '__main__':
	main()
