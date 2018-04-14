'use strict';

const mongoose = require('mongoose');

let Schema = mongoose.Schema;
let cardSchema = new Schema({
    bookId: Number,
    bookName: String,
    author: String,
    year: Number,
    publisher: String,
    bookDescription: String,
    ownerId: Number,
    createDate: Date
});

cardSchema.index({ bookId: 1 }, { unique: true });

module.exports = mongoose.model('Card', cardSchema);