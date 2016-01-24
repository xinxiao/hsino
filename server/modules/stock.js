// ---------------------------------------------------------------------------- //
// Stock Schema
//
// Author: Xiao Xin
// Date: Jan. 23, 2016
// ---------------------------------------------------------------------------- //

/*
	Import dependencies
*/
var mongoose = require('mongoose');
var Schema = mongoose.Schema;

/*
	Set up schema
*/
var StockSchema = new Schema({
		exchange : String,
		ticker : String,
		company : String,
		location : String,
		currency : String,
		detail : mongoose.Schema.Types.Mixed
	},{
		collection : 'Stock'
	});

module.exports = mongoose.model('Stock', StockSchema);				// Return schema
