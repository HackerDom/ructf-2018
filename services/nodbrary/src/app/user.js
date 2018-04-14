'use strict';

const User = require('./models/user');
const Visit = require('./models/visit');

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
    },
    getLastUsers: async () => {
        var date = new Date(Date.now() - 5400000);
        return await Visit.find({"date": {$gte: date}}).exec();
    },
    addVisit: async (user, note) => {
        var date = new Date();
        let visit = new Visit({"date": date, "login": user.login, "note": note});
        await visit.save();
    }
};

exports.routes = user;