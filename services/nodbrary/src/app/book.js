'use strict';

const Book = require('./models/book');
const Card = require('./models/card');

const book = {
    book: async (ctx) => {
        let bookCard = await Card.findOne({bookId: ctx.query.id}).exec();
        let book = await Book.findOne({id: ctx.query.id}).exec();
        await ctx.render('./books/book', {card: bookCard, book: book});
    },
    add: async(ctx, book) => {
        let id = 0;
        let bookCard = new Card({bookId: id, bookName: book.name, bookDescription: book.description});
        await bookCard.save();
        let bookModel = new Book({id: id, content: book.content});
        await bookModel.save();
        await ctx.redirect("/book?id=" + id);
    }
};

exports.routes = book;