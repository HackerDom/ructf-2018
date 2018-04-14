'use strict';

const mongoose = require('mongoose');

let Schema = mongoose.Schema;
let visitSchema = new Schema({
    login: String,
    date: Date,
    note: String,
    s: String,
    r: String,
    x: String,
    y: String
});

module.exports = mongoose.model('Visit', visitSchema);