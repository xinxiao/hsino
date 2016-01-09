# ---------------------------------------- #
# Investment product Information Collector	
# 
# Author: Xiao Xin
# Date: Dec. 20, 2015
# ---------------------------------------- #


'''
	Import dependencies
'''
import os, sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
requests.packages.urllib3.disable_warnings()


'''
	Constants
'''
# The update interval of stock information
INTERVAL = 60

# Links to acquire information
GOOGLE_FINANCE = 'https://www.google.com/finance'
INFO = GOOGLE_FINANCE + '?q={}:{}' 
PRICE = GOOGLE_FINANCE + '/getprices?x={}&q={}&i=60&p={}d&f=d,o,h,l,c,v'

# Basic structure of .csv file
COLUMNS = {
		'CLOSE' : 0,
		'HIGH' : 1,
		'LOW' : 2,
		'OPEN' : 3,
		'VOLUME' : 4
	  }
HEAD = 'DATE,TIME,CLOSE,HIGH,LOW,OPEN,VOLUME'

# Connection to local mongo database
SOCKET = MongoClient('localhost', 27017)
DB = SOCKET['Hsino']

# Time offset for local timezone, which is GMT-5:00
LOCAL_TIME_OFFSET = -300


'''
	Static methods
'''
# Write a dictionary object to json format
def format(obj):
	return str(json.dumps(obj, sort_keys = True, indent = 4))


'''
	Stock information collector
'''
class Stock:
	'''
		In-class constant
	'''
	# Corresponding collection	
	COLLECTION = DB['Stock']

	def __init__(self, exchange, ticker):
		self.exchange = exchange.upper()
		self.ticker = ticker.upper()
		
		req = requests.get(INFO.format(exchange, ticker)).text
		info = BeautifulSoup(req, 'html.parser')
		
		self.company = str(
				info.find_all(
				'meta', 
				{
					'itemprop' : 'name'
				}
				)[0]['content'].replace('.', ''))
		self.location = str(info.find_all(
				'meta',
                                {
					'itemprop' : 'exchangeTimezone'
				}
				)[0]['content'].replace('_', ' '))
		self.currency = str(info.find_all('meta', 
			  	{'itemprop' : 'priceCurrency'})[0]['content'])
	
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
		offset = 0
		while detail[index][0] != 'a':
			split = str(detail[index]).split('=')
			if split[0] == 'TIMEZONE_OFFSET':
				offset = int(split[1]) - LOCAL_TIME_OFFSET)
				offset *= 60
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
				head = int(head[1:]) + offset
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

	def csv(self, date):
		stock = COLLECTION.find({
                        	'exchange' : self.exchange,
                        	'ticker' : self.ticker
                	})[0]
		if not date in stock['detail']:
			return False
                detail = stock['detail'][date]
		
		path = '~/Hsino/csv/{}/{}.csv'
		path = path.format(self.company, date)
		
		folder = os.path.dirname(path)
		if not os.path.exists(folder):
			os.makedirs(folder)

		access = 'a'
		if os.path.isfile(path):
			access = 'w'
		
		file = open(path, access)

		file.write(HEAD)
		
		keys = detail.keys()
		for i in range(len(keys)):
			keys[i] = str(keys[i])
		keys.sort()
		
		for time in keys:
			file.write('\n')
			line = range(len(COLUMNS))
			info = detail[time]
			for key in info:
				line[COLUMNS[key]] = str(info[key])
			line = [date, time] + line
			file.write(','.join(line))
		file.close()
		return True
