'use strict';

const Router = require('koa-router');
const KoaBody = require('koa-body');
const convert = require('koa-convert');
const passport = require('koa-passport');
let router = new Router();
let koaBody = convert(KoaBody());
let catalog = require('../app/catalog').routes;
let book = require('../app/book').routes;
let user = require('../app/user').routes;
let validator = require('../app/inputValidator').validator;
let ValidationError = require('../app/inputValidator').ValidationError;

router
    .use('/book', async (ctx, next) => {
        if (!ctx.query.id)
            await ctx.render('./service/404');
        await next();
    });

router
    .get(['/', '/home'], async (ctx, next) => {
        let bookCards = await catalog.catalog();
        await ctx.render('./books/catalog', {cards: bookCards});
        await next();
    })
    .get('/book', async (ctx, next) => {
        let response = await book.book(ctx.query.id);
        await ctx.render('./books/book', response);
        await next();
    })
    .get('/create', async (ctx, next) => {
        await ctx.render("./books/create", {params: {name: "", author: "", year: 2000, publisher: "", description: "", content: ""}});
        await next();
    })
    .post('/add', koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let bookModel = {};
                bookModel.name = validator.validateString(body.name, "Название книги");
                bookModel.author = validator.validateString(body.author, "Автор");
                bookModel.year = validator.validateNumber(body.year, "Год");
                bookModel.publisher = validator.validateString(body.publisher, "Издатель");
                bookModel.description = validator.validateString(body.description, "Описание книги");
                bookModel.content = validator.validateString(body.content, "Текст книги");
                ctx.state.body = bookModel;
                await next();
            } catch(e) {
                if (e instanceof ValidationError)
                    await ctx.render("./books/create", {error: e.message, params: body});
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let body = ctx.request.body;
            let bookId = await book.add(body);
            await ctx.redirect("/book?id=" + bookId);
            await next();
        })
    .get('/signin', async (ctx, next) => {
        await ctx.render("./users/signin", {params: {login: "", pass: ""}});
        await next();
    })
    .post('/signin', koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let userSignInModel = {};
                userSignInModel.login = validator.validateLogin(body.login);
                userSignInModel.pass = validator.validatePass(body.pass);
                ctx.state.body = userSignInModel;
                await next();
            } catch(e) {
                ctx.status = 403;
                if (e instanceof ValidationError)
                    await ctx.render("./users/signin", {error: e.message, params: ctx.request.body});
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            await passport.authenticate('local', async(err, user) => {
                if(!user){
                    await ctx.render("./users/signin", { error: "Неверный логин или пароль", params: ctx.request.body });
                } else {
                    await ctx.login(user);
                    await ctx.redirect('/');
                    await next();
                }
            })(ctx);
        })
    .get('/signup', async (ctx, next) => {
        await ctx.render("./users/signup", {params: {login: "", pass: "", passConfirm: ""}});
        await next();
    })
    .post('/signup', koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let userSignUpModel = {};
                userSignUpModel.login = validator.validateLogin(body.login);
                userSignUpModel.pass = validator.validatePass(body.pass);
                userSignUpModel.passConfirm = validator.validatePass(body.passConfirm);
                ctx.state.body = userSignUpModel;
                await next();
            } catch(e) {
                if (e instanceof ValidationError)
                    await ctx.render("./users/signup", {error: e.message, params: body});
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let body = ctx.state.body;
            if (body.pass != body.passConfirm)
                await ctx.render("./users/signup", {error: "Поле подтверждение пароля не совпадает с полем пароль", params: ctx.request.body});
            else
                await next();
        },
        async (ctx, next) => {
            let body = ctx.state.body;
            if (await user.isExist(body.login))
                await ctx.render("./users/signup", {error: "Такой пользователь уже существует", params: ctx.request.body});
            else
                await next();
        },
        async (ctx, next) => {
            let body = ctx.state.body;
            var userModel = await user.signup(body);
            await ctx.login(userModel);
            await ctx.redirect("/");
            await next();
        })
    .get('/logout', async (ctx, next) => {
        ctx.logout();
        await ctx.redirect("/");
        await next();
    });

exports.routes = () => { return router.routes() };
exports.allowedMethods = () => { return router.allowedMethods() };