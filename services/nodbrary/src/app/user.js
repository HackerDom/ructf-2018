'use strict';

const User = require('./models/user');
const Visit = require('./models/visit');

const user = {
    signup: async (userModel) => {
        userModel = new User(userModel);
        return await userModel.save();
    },
    isExist: async (login) => {
        return (await User.find({login: login}).exec()).length > 0;
    },
    findUser: async (login) => {
        return await User.find({login:login}).exec();
    },
    getLastUsers: async () => {
        var date = new Date(Date.now() - 15*60*1000);
        return await Visit.find({"date": {$gte: date}}).exec();
    },
    addVisit: async (body) => {
        var date = new Date();
        let visit = new Visit({
            "date": date, 
            "login": body.user.login, 
            "note": body.note, 
            "r": body.sign[0].toString(16),
            "s": body.sign[1].toString(16),
            "x": body.user.keyX,
            "y": body.user.keyY
        });
        await visit.save();
    }
};

exports.routes = user;