'use strict';

const mongoose = require('mongoose');

let Schema = mongoose.Schema;
let cardSchema = new Schema({
    bookName: String,
    bookId: Number,
    bookDescription: String
});

module.exports = mongoose.model('Card', cardSchema);