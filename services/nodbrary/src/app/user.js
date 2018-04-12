'use strict';

const User = require('./models/user');

const user = {
    signup: async (user, key) => {
        let userModel = new User({
            login: user, 
            keyX: key.getX().toString(16), 
            keyY: key.getY().toString(16)
        });
        return await userModel.save();
    },
    isExist: async (login) => {
        return (await User.find({login: login}).exec()).length > 0;
    },
    findUser: async (login) => {
        return await User.find({login:login}).exec();
    }
};

exports.routes = user;