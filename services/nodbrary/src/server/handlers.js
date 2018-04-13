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
        await ctx.redirect('./home/1');
        await next();
    })
    .get('/home/:page',
        async (ctx, next) => {
            try {
                ctx.state.page = validator.validateNumber(ctx.params.page);
                if (!ctx.state.page || ctx.state.page <= 0)
                    throw new ValidationError();
                await next();
            } catch(e) {
                if (e instanceof ValidationError)
                    await ctx.redirect("/");
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let currentPage = ctx.state.page;
            let bookCards = await catalog.catalog();
            let pagesCount = Math.ceil(bookCards.length / 9);
            if (pagesCount > 0 && pagesCount < currentPage)
                await ctx.redirect("/");
            let pages = Array.apply(null, {length: pagesCount}).map((n, i) => i + 1);

            await ctx.render('./books/catalog', {
                cards: bookCards.slice(9*(currentPage-1), 9*(currentPage)),
                pages: pages,
                nextPage: currentPage + 1,
                previousPage: currentPage - 1,
                isAuthenticated: ctx.isAuthenticated()
            });
            await next();
        })
    .get('/book/:id',
        async (ctx, next) => {
            try {
                ctx.state.id = validator.validateNumber(ctx.params.id);
                if (ctx.state.id < 0)
                    throw new ValidationError();
                await next();
            } catch(e) {
                if (e instanceof ValidationError)
                    await ctx.redirect("./service/404");
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let result = await book.book(ctx.state.id);
            let tags = null;
            let auth = false;
            if (ctx.isAuthenticated()) {
                tags = await book.tags(ctx.state.user.id, ctx.state.id);
                auth = true;
            }
            if (!result)
                await ctx.redirect(".//service/404");
            await ctx.render('./books/book', {book: result, tags: tags, auth: auth});
            await next();
        })
    .get('/create',
        async (ctx, next) => {
            if (!ctx.isAuthenticated())
                await ctx.render("./service/404");
            else
                await next()
        },
        async (ctx, next) => {
            await ctx.render("./books/create", { params: { name: "", author: "", year: 2000, publisher: "", description: "", content: "" }});
            await next();
        })
    .post('/add',
        async (ctx, next) => {
            if (!ctx.isAuthenticated())
                await ctx.render("./service/404");
            else
                await next()
        },
        koaBody,
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
    })
    .post('/tag',
        async (ctx, next) => {
            if (!ctx.isAuthenticated())
                ctx.response.status = 403;
            else
                await next()
        }, koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let bookId = validator.validateNumber(body.bookId);
                let tag = validator.validateString(body.tag);
                if (tag.length > 20)
                    throw new ValidationError("");
                ctx.state.body = {bookId: bookId, tag: tag};
                await next();
            } catch(e) {
                if (e instanceof ValidationError)
                    ctx.response.status = 404;
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            book.addTag(ctx.state.user.id, ctx.state.body.bookId, ctx.state.body.tag);
            ctx.response.status = 200;
            await next();
        });

exports.routes = () => { return router.routes() };
exports.allowedMethods = () => { return router.allowedMethods() };