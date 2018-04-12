'use strict';

const Book = require('./models/book');
const Card = require('./models/card');
const User = require('./models/user');

const book = {
    book: async (id) => {
        let bookCard = await Card.findOne({bookId: id}).exec();
        let book = await Book.findOne({id: id}).exec();
        let user = await User.findOne({id: bookCard.ownerId}).exec();
        return {book: {
            name: bookCard.bookName,
            author: bookCard.author,
            year: bookCard.year,
            publisher: bookCard.publisher,
            description: bookCard.bookDescription,
            owner: user.login,
            date: bookCard.createDate,
            content: book.content
        }};
    },
    add: async (bookParameters, userId) => {
        let bookModel = new Book({content: bookParameters.content});
        await bookModel.save();
        let bookCard = new Card({
            bookId: bookModel.id,
            bookName: bookParameters.name,
            author: bookParameters.author,
            year: bookParameters.year,
            publisher: bookParameters.publisher,
            bookDescription: bookParameters.description,
            ownerId: userId,
            createDate: new Date()
        });
        await bookCard.save();
        return bookModel.id;
    }
};

exports.routes = book;