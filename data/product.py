# ---------------------------------------------------------------------------- #
# Hsino Fianacial Information Collector	
# 
# Author: Xiao Xin
# Date: Dec. 20, 2015
# ---------------------------------------------------------------------------- #


'''
	Import dependencies
'''
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
GOOGLE_FINANCE = 'http://www.google.com/finance'
INFO = GOOGLE_FINANCE + '?q={}:{}'
PRICE = GOOGLE_FINANCE + '/getprices?x={}&q={}&i=60&p={}d&f=d,o,h,l,c,v'

# Basic structure of data
COLUMNS = {
		'CLOSE' : 0,
		'HIGH' : 1,
		'LOW' : 2,
		'OPEN' : 3,
		'VOLUME' : 4,
		'PRICE CHANGE' : 5,
		'VOLUME CHANGE' : 6
	  }

# Connection to local mongo database
SOCKET = MongoClient('localhost', 27017)
DB = SOCKET['Hsino']

# Time offset for local timezone, which is GMT-5:00
LOCAL_TIME_OFFSET = -300

'''
	Stock information collector
'''
class Stock:
	'''
		In-class constant
	'''
	# Corresponding collection	
	COLLECTION = DB['Stock']

	# Constructor
	def __init__(self, exchange, ticker):
		# Save ticker number and exchange
		self.exchange = exchange.upper()
		self.ticker = ticker.upper()
		
		# Request more detailed information from Google Finance
		req = requests.get(INFO.format(exchange, ticker)).text
		info = BeautifulSoup(req, 'html.parser')
		meta = info.find_all('meta')		

		# Extract information from google Finance 
		self.company = str(
				info.find_all(
				'meta', 
				{
					'itemprop' : 'name'
				}
				)[0]['content'].replace('.', ''))		# Find company name
		self.location = str(info.find_all(
				'meta',
                                {
					'itemprop' : 'exchangeTimezone'
				}
				)[0]['content'].replace('_', ' '))		# Find the location of exchange
		self.currency = str(info.find_all('meta', 
			  	{'itemprop' : 'priceCurrency'}
				)[0]['content'])				# Find out the pricing currency
	
	# Representation
	def __repr__(self):
		info = self.info()						# Get info package
		result = []
		for field in info:
			result += ["{}: {}".format(field, info[field])]		# Put each field in format
		return '\n'.join(result)					# Put info in paragraph

	# Check if the stock has been stored in local database
	def has_stored(self):
		cursor = Stock.COLLECTION.find({
                        	'exchange' : self.exchange,
                        	'ticker' : self.ticker
                	 })							# Look for stock in database
		
		return cursor.count() > 0					# Return true if stock were found

	# Return a dictionary of  the general information of the stock
	def info(self):
		stock = {
				'exchange' : self.exchange,
				'ticker' : self.ticker,
				'company' : self.company,
				'location' : self.location,
				'currency' : self.currency
			}							# Put information in dictionary

		return stock
	
	# Acquire the trading data of given recent days
	#
	# The update frequency of the data is set to be 1 update per 
	# minute, for this value to be the highest frequency allowed by 
	# Google Finance serveice
	def detail(self, period):
		# Request trading data
		detail = str(requests.get(
				PRICE.format(self.exchange,
					     self.ticker, period),
				verify = False 
			  ).text).split('\n')[:-1]
		
		# Processing the header of the request	
		index = 1 
		offset = 0
		while detail[index][0] != 'a':					# Loop to data
			split = str(detail[index]).split('=')
			if split[0] == 'TIMEZONE_OFFSET':			# Look for timezone offset
				offset = int(split[1]) - LOCAL_TIME_OFFSET
				offset *= 60
			index += 1
			if index >= len(detail):
				return {}					# Terminate if no data were found
		detail = detail[index:]						# Cut off header
		
		# Processing actual data
		index = 0
		stamp = 0
		date = ''
		previous_volume = 0
		result = {}
		while index < len(detail):					# Loop to end
			split = detail[index].split(',')			# Split terms
			head = split[0]						# Get the first term
			split = split[1:]					# Save the rest
	
			# Check if a new date stamp appears	
			if head[0] == 'a':					# If a new date stamp were found
				head = int(head[1:]) + offset			# Parse date stamp;
										# add time offset

				stamp = head					# Reset date stamp
				date = datetime.fromtimestamp(
						stamp
					).strftime('%Y-%m-%d')			# Put date in proper format
				previous_volume = int(split[-1])		# Set initial previous volume
				result[date] = {}				# Set field in result for this dat
			else:							# If no new date stamp were found
				head = stamp + int(head) * INTERVAL		# Calculate exact timestamp

			time = datetime.fromtimestamp(
					head
				).strftime('%H:%M')				# Calculate when data appears
			
			for i in range(len(split) - 1):				# Parse each numeric value
				split[i] = float(split[i])
			split[-1] = int(split[-1])			
			
			open_price = split[COLUMNS['OPEN']]
			close_price = split[COLUMNS['CLOSE']]
			price_change = (close_price / open_price - 1) * 100	# Calculate the price change
			
			volume = split[COLUMNS['VOLUME']]
			volume_change = float(volume) / float(previous_volume)
			volume_change = 100 * (volume_change - 1)		# Calculate volume change 
			previous_volume = volume				# Reset previous volume
			
			split += [price_change, volume_change]			# Save calculated value in line

			content = {}						# Put data into term
			for key in COLUMNS:
				content[key] = split[COLUMNS[key]]

			result[date][time] = content				# Save the data at the time point 
			index += 1

		return result
	
	# Save the trading data of given recent days
	def store(self, period):
		# Check if the stock had been previously stored in database
		if not self.has_stored():					# If the stock has not been stored
			info = self.info()					# Create stock general info header
			info['detail'] = {}
			Stock.COLLECTION.insert_one(info)			# Insert stock info into database 

		stock = Stock.COLLECTION.find({
				'exchange' : self.exchange,
				'ticker' : self.ticker
			})[0]							# Find the stored stock
		
		detail = stock['detail']
		update = self.detail(period)					# Find the updating portion 

		for key in update:
			detail[key] = update[key]				# Update the info of each day
		
		result = Stock.COLLECTION.update_one(
			{
				'exchange' : self.exchange,
				'ticker' : self.ticker,

			},
			{ '$set' : { 'detail' : detail } },
		)								# Store the data in database

