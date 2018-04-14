'use strict';

const Card = require('./models/card');

const catalog = {
    catalog: async () => {
        return await Card.find({}).exec();
    },
};

exports.routes = catalog;