'use strict';

const mongoose = require('mongoose');
const autoIncrement = require('mongoose-auto-increment');
autoIncrement.initialize(mongoose.connection);

let Schema = mongoose.Schema;
let bookSchema = new Schema({
    id: Number,
    content: String
});

bookSchema.index({ id: 1 }, { unique: true });

bookSchema.plugin(autoIncrement.plugin, {model: 'Book', field: 'id'});
module.exports = mongoose.model('Book', bookSchema);