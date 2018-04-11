'use strict';

const User = require('./models/user');

const user = {
    signup: async (user) => {
        let userModel = new User({login: user.login, pass: user.pass});
        await userModel.save();
    },
    signin: async (user) => {
        return await User.findOne({login: user.login, pass: user.pass}).exec();
    },
    isExist: async (login) => {
        return (await User.find({login: login}).exec()).length > 0;
    }
};

exports.routes = user;