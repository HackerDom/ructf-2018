'use strict';

const User = require('./models/user');

const book = {
    signup: async (user) => {
        let userModel = new User({login: user.login, pass: user.pass});
        await userModel.save();
    },
    signin: async (user) => {
        return await User.findOne({login: user.login, pass: user.pass}).exec();
    },
};

exports.routes = book;