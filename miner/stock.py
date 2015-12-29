import os, sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

INTERVAL = 60
GOOGLE_FINANCE = 'https://www.google.com/finance'
INFO = GOOGLE_FINANCE + '?q={}:{}' 
PRICE = GOOGLE_FINANCE + '/getprices?x={}&q={}&i=60&p={}d&f=d,o,h,l,c,v'

COLUMNS = {
		'CLOSE' : 0,
		'HIGH' : 1,
		'LOW' : 2,
		'OPEN' : 3,
		'VOLUME' : 4
	  }
HEAD = 'DATE,TIME,CLOSE,HIGH,LOW,OPEN,VOLUME'

SOCKET = MongoClient('localhost', 27017)
DB = SOCKET['Hsino']
COLLECTION = DB['Stock']

def main():
	msft = Stock('NASDAQ', 'MSFT')
	print msft.store(2)

class Stock:
	def __init__(self, exchange, ticker):
		self.exchange = exchange
		self.ticker = ticker
		
		req = requests.get(INFO.format(exchange, ticker)).text
		info = BeautifulSoup(req, 'html5lib')
		
		self.company = info.find_all(
				'meta', 
				{
					'itemprop' : 'name'
				}
				)[0]['content'].replace('.', '')
		self.location = info.find_all(
				'meta',
                                {
					'itemprop' : 'exchangeTimezone'
				}
				)[0]['content'].replace('_', ' ')
		self.currency = info.find_all('meta', 
			  	{'itemprop' : 'priceCurrency'})[0]['content']
	
	def __repr__(self):
		return format(self.info())

	def is_stored(self):
		cursor = COLLECTION.find({
                        	'exchange' : self.exchange,
                        	'ticker' : self.ticker
                	 })

		count = 0
		for element in cursor:
			count += 1
		
		return count > 0
		
	def info(self):
		stock = {
				'exchange' : self.exchange,
				'ticker' : self.ticker,
				'company' : self.company,
				'location' : self.location,
				'currency' : self.currency
			}

		return stock
	
	def detail(self, period):
		detail = str(requests.get(
				PRICE.format(self.exchange,
					     self.ticker, period)
			  ).text).split('\n')
		
		index = 1 
		header = {}
		while detail[index][0] != 'a':
			index += 1
		detail = detail[index:-1]
		
		index = 0
		stamp = 0
		date = ''
		result = {}
		while index < len(detail):
			split = detail[index].split(',')
			head = split[0]
			split = split[1:]

			if head[0] == 'a':
				head = int(head[1:])
				stamp = head 
				date = datetime.fromtimestamp(
					stamp
				      ).strftime('%Y-%m-%d')
				result[date] = {}
			else:
				head = stamp + int(head) * INTERVAL

			time = datetime.fromtimestamp(
					head
				).strftime('%H:%M')
			
			for i in range(len(split) - 1):
				split[i] = float(split[i])
			split[-1] = int(split[-1])
			
			content = {}
			for key in COLUMNS:
				content[key] = split[COLUMNS[key]]

			result[date][time] = content
			index += 1

		return result
	
	def store(self, period):
		if not self.is_stored():
			info = self.info()
			info['detail'] = {}
			COLLECTION.insert_one(info)

		stock = COLLECTION.find({
			'exchange' : self.exchange,
			'ticker' : self.ticker
		})[0]
		print stock	
		
		detail = stock['detail']
		update = self.detail(period)

		for key in update:
			detail[key] = update[key]
		
		result = COLLECTION.update_one(
			{
				'exchange' : self.exchange,
				'ticker' : self.ticker,

			},
			{ '$set' : { 'detail' : detail } },
		)

		return result.modified_count > 0	

#	def csv(self, period):
#		detail = str(requests.get(
#				PRICE.format(self.exchange,
#				self.ticker, period)
#			).text).split('\n')
#
#		index = 0
#		while detail[index][0] != 'a':
#			index += 1
#		detail = detail[index:-1]
#
#		path = './data/{}.csv'.format(self.company)
#		accessibility = 'a'
#		if os.path.isfile(path):
#			accessibility = 'w'
#
#		file = open(path, accessibility)
#		file.write(HEAD)
#
#		stamp = 0
#		date = ''		
#		for index in range(len(detail)):
#			file.write('\n')
#			split = detail[index].split(',')
#			head = split[0]
#			split = split[1:]
#			if head[0] == 'a':
#				head = int(head[1:])
#				stamp = head
#				date = datetime.fromtimestamp(
#						stamp
#					).strftime('%Y-%m-%d')
#			else:
#				head = stamp + int(head) * INTERVAL
#
#			time = datetime.fromtimestamp(
#                                        head
#                                ).strftime('%H:%M')
#
#			file.write(date + ',' + 
#				   time + ',' + 
#				   ','.join(split))			
#		file.close()

if __name__ == '__main__':
	main()
