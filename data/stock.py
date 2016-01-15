# ---------------------------------------------------------------------------- #
# Investment Product Information Collector	
# 
# Author: Xiao Xin
# Date: Dec. 20, 2015
# ---------------------------------------------------------------------------- #


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
COLLECTION = DB['Stock']

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
	# COLLECTION = DB['Stock']

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
				)[0]['content'].replace('_', ' '))		# Find the location of the exchange
		self.currency = str(info.find_all('meta', 
			  	{'itemprop' : 'priceCurrency'}
				)[0]['content'])				# Find out the pricing currency
	
	# Representation
	def __repr__(self):
		return format(self.info())

	# Check if the stock has been stored in local database
	def has_stored(self):
		cursor = COLLECTION.find({
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
			  ).text).split('\n')
		
		# Processing the header of the request	
		index = 1 
		header = {}
		offset = 0
		while detail[index][0] != 'a':					# Loop to data
			split = str(detail[index]).split('=')
			if split[0] == 'TIMEZONE_OFFSET':			# Look for timezone offset
				offset = int(split[1]) - LOCAL_TIME_OFFSET
				offset *= 60
			index += 1
		detail = detail[index:-1]					# Cut off header
		
		# Processing actual data
		index = 0
		stamp = 0
		date = ''
		result = {}
		while index < len(detail):					# Loop to end
			split = detail[index].split(',')			# Split terms
			head = split[0]						# Get the first term
			split = split[1:]					# Save the rest
			
			# Check if a new date stamp appears	
			if head[0] == 'a':					# If a new date stamp were found
				head = int(head[1:]) + offset			# Parse date stamp; add time offset
				stamp = head					# Reset date stamp
				date = datetime.fromtimestamp(
						stamp
					).strftime('%Y-%m-%d')			# Put date in proper format
				result[date] = {}				# Set field in result for this dat
			else:							# If no new date stamp were found
				head = stamp + int(head) * INTERVAL		# Calculate exact timestamp

			time = datetime.fromtimestamp(
					head
				).strftime('%H:%M')				# Calculate the time when data occurs
			
			for i in range(len(split) - 1):				# Parse each numeric value
				split[i] = float(split[i])
			split[-1] = int(split[-1])			
			
			content = {}						# Put data into term
			for key in COLUMNS:
				content[key] = split[COLUMNS[key]]

			result[date][time] = content				# Save the data for the time point 
			index += 1

		return result
	
	def find(self, date):
		if not self.has_stored():
			return False, None					# Return false and nothing if the stock
										# has not been stored

		data = COLLECTION.find({
                                'exchange' : self.exchange,
                                'ticker' : self.ticker
                        })[0]['detail']						# Find the stored part of the stock
		
		if date not in data:
			return False, None					# Return false if the data of a certain day
										# has not been stored

		return True, data[date]						# Return true as result and stock data
	
	# Save the trading data of given recent days
	def store(self, period):
		# Check if the stock had been previously stored in database
		if not self.has_stored():					# If the stock has not been stored
			info = self.info()					# Create stock general info header
			info['detail'] = {}
			COLLECTION.insert_one(info)				# Insert stock info into database 

		stock = COLLECTION.find({
				'exchange' : self.exchange,
				'ticker' : self.ticker
			})[0]							# Find the stored part of the stock
		print stock	
		detail = stock['detail']
		update = self.detail(period)					# Acquire the data that needs storing

		for key in update:
			detail[key] = update[key]				# Update the info of each day
		
		result = COLLECTION.update_one(
			{
				'exchange' : self.exchange,
				'ticker' : self.ticker,

			},
			{ '$set' : { 'detail' : detail } },
		)								# Put the data in database

	# Export trading data of a given date to .csv file
	#
	# Return if the file has been generated 
	def csv(self, date):
		found, detail = self.find(date)					# Check if the stock info has been stored
		
		if not found:
			return False						# Terminate if no data were found
 
		path = '~/Hsino/csv/{}/{}.csv'					# Set the path of file
		path = path.format(self.company, date)
		
		folder = os.path.dirname(path)					# Check if directories on path exists
		if not os.path.exists(folder):
			os.makedirs(folder)					# Make directories if needed

		access = 'a'							# Set initial accessibility to append
		if os.path.isfile(path):
			access = 'w'						# Update the file if files exists
		
		file = open(path, access)					# Open file

		file.write(HEAD)						# Write head of .csv file
		
		keys = detail.keys()
		for i in range(len(keys)):
			keys[i] = str(keys[i])
		keys.sort()							# Sort the trading data by time
		
		for time in keys:						# Write data of every minute to file
			file.write('\n')					# Switch line at the begining
										# in case new line at very end
			line = range(len(COLUMNS))				# Prepare to combine data components
			info = detail[time]					# Get data at time point
			for key in info:
				line[COLUMNS[key]] = str(info[key])		# Put each field in position
			line = [date, time] + line				# Add date and time
			file.write(','.join(line))				# Join the conponents by comma, 
										# and write to file
		file.close()							# Close file
		return True							# Return True for file has been
										# successfully generated
