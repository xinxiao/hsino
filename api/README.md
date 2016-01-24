# Hsino Financial Data API

### Introduction
This information exchange service is written to deliver the data collected by Hsino data collectors to the researchers

### Data architecture
This interface is designed under the concept of "read-only" RESTful. Users are given only the rights to read data from the database, but not the rights to write data to local database or delete data from local database

### Address of service
- IP:		137.112.40.145, virtual machine hosted by Rose-Hulman Institute of Technology
- Port:		1031, to memorize the author, who is me, of the script

### Methods and parameters
- GET: exchange/ticker
	- Return the following information of the stock
		- Name of the company who issues the stock
 		- Location of the exchange
 		- Currency in which the stock trades
- POST: exchange/ticker/date
	- Return the minutely trading data of the stock on the given date only if the trading data is stored in local database
	
