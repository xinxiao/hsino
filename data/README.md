# Hsino Data Collector

### Source of data
[Google Finance](https://www.google.com/finance)

### Purpose of the script
Google Finance only reserve the minutely trading data of a stock within 15 days. The script is used as a buffer to save trading data of a longer period for researchers to discover possible correlation patterns in financial trading.

### Data components
- Open price
- Close price
- Highest price
- Lowest price
- Total trading volume
- Percentage of price change
- Percentage of trading volume change

#### Script Components
This collector is now composed of two major scripts:
- Product, which is used to collected the trading data of financial products. It could be used to collect the data of
	- Stock
	- Bond (To be implemented)
	- Currency (To be implemented)
	- Future (To be implemented)
- Update, which is used to constantly update the trading data in local database

### Methods
- Stock(exchange, ticker): Construct a stock object to explore trading data online
- info(): Output the following general information a the stock
	- Name of the company who issues the stock
	- Name of the exchange where it trades
	- Ticker symbol of the stock at the exchange
	- Location of the exchange
	- Currency in which the stock trades
- detail(period): Searching for the trading data within the given period
- store(period): Store the trading data within the given period into local database
