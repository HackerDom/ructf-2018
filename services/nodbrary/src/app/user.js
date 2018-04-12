'use strict';

const User = require('./models/user');

const user = {
    signup: async (user) => {
        let userModel = new User({
            login: user.login, 
            keyX: user.key.getX().toString(16), 
            keyY: user.key.getY().toString(16)
        });
        return await userModel.save();
    },
    isExist: async (login) => {
        return (await User.find({login: login}).exec()).length > 0;
    }
};

exports.routes = user;