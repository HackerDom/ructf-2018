'use strict';

const User = require('./models/user');

const user = {
    signup: async (user) => {
        let userModel = new User({login: user.login, pass: user.pass});
        return await userModel.save();
    },
    isExist: async (login) => {
        return (await User.find({login: login}).exec()).length > 0;
    }
};

exports.routes = user;