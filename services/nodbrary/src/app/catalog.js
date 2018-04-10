'use strict';

const Card = require('./models/card');

const catalog = {
    catalog: async (ctx) => {
        let bookCards = await Card.find({}).exec();
        await ctx.render('./books/catalog', {cards: bookCards});
    },
};

exports.routes = catalog;