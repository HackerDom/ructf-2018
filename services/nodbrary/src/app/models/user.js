'use strict';

const mongoose = require('mongoose');
const autoIncrement = require('mongoose-auto-increment');
autoIncrement.initialize(mongoose.connection);

let Schema = mongoose.Schema;
let userSchema = new Schema({
    id:  Number,
    login: String,
    keyX: String,
    keyY: String
});

userSchema.index({ id: 1, login: 1 }, { unique: true });

userSchema.plugin(autoIncrement.plugin, {model: 'User', field: 'id'});
module.exports = mongoose.model('User', userSchema);