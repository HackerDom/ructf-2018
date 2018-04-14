'use strict';

const mongoose = require('mongoose');

let Schema = mongoose.Schema;

let tagSchema = new Schema({
    userId: Number,
    bookId: Number,
    tags: [String]
});

tagSchema.index({ userId: 1, bookId: 1 }, { unique: true });

module.exports = mongoose.model('Tag', tagSchema);