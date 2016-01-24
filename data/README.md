# Hsino Financial Data Collector

### Source of data
[Google Finance](https://www.google.com/finance), which has the ability to provide minutely updated trading data of a certain stock within the most recent 15 days. 

### Purpose
Google Finance only reserve the minutely trading data of a stock within 15 days. The script is used as a buffer to save trading data of a longer period for researchers to discover possible correlation patterns in financial trading.

### Data components
- Stock
	* Open price
	* Close price
	* Highest price
	* Lowest price
	* Total trading volume
	* Percentage of price change
	* Percentage of trading volume change

#### Script Components
- Product, which is used to collected the trading data of financial products. It could be used to collect the trading data of:
	* Stock
	* Bond		(To be implemented)
	* Currency 	(To be implemented)
	* Future 	(To be implemented)
- Update, which is used to constantly update the trading data of a given portfolio in local database

### Methods
- Stock(exchange, ticker): Construct a stock object to explore trading data online
- Stock.info(): Output the following general information a the stock
	* Name of the company who issues the stock
	* Name of the exchange where the stock trades
	* Ticker symbol of the stock at the exchange
	* Location of the exchange
	* Currency in which the stock trades
- Stock.detail(period): Searching for the trading data within the given period
- Stock.store(period): Store the trading data within the given period into local database
