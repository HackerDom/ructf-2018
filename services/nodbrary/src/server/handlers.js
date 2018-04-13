'use strict';

const Router = require('koa-router');
const KoaBody = require('koa-body');
const convert = require('koa-convert');
const passport = require('koa-passport');
const superEC = require('../app/super-ec');
let router = new Router();
let koaBody = convert(KoaBody());
let catalog = require('../app/catalog').routes;
let book = require('../app/book').routes;
let user = require('../app/user').routes;
let validator = require('../app/inputValidator').validator;
let ValidationError = require('../app/inputValidator').ValidationError;
let curve = new superEC();

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
                if (e instanceof ValidationError) {
                    ctx.response.status = 404;
                    ctx.redirect('/home/1')
                }
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let currentPage = ctx.state.page;
            let bookCards = await catalog.catalog();
            let pagesCount = Math.ceil(bookCards.length / 9);
            if (pagesCount > 0 && pagesCount < currentPage)
                await ctx.redirect("/home/" + pagesCount);
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
                    ctx.response.status = 404;
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
            console.log(result)
            if (!result) {
                ctx.response.status = 404;
                return
            }
            await ctx.render('./books/book', {book: result.book, tags: tags, auth: auth});
            await next();
        })
    .get('/create',
        async (ctx, next) => {
            if (!ctx.isAuthenticated())
                ctx.response.status = 403;
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
                ctx.response.status = 403;
            else
                await next()
        },
        koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let bookModel = {};
                bookModel.name = validator.validateString(body.name, "Book name");
                bookModel.author = validator.validateString(body.author, "Author");
                bookModel.year = validator.validateNumber(body.year, "Year");
                bookModel.publisher = validator.validateString(body.publisher, "Publisher");
                bookModel.description = validator.validateString(body.description, "Book Description");
                bookModel.content = validator.validateString(body.content, "Book Content");
                ctx.state.body = bookModel;
                await next();
            } catch(e) {
                ctx.response.status = 400;
                if (e instanceof ValidationError)
                    await ctx.render("./books/create", {error: e.message, params: body});
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let body = ctx.request.body;
            let bookId = await book.add(body, ctx.state.user.id);
            await ctx.redirect("/book/" + bookId);
            await next();
        })
    .get('/signin', async (ctx, next) => {
        await ctx.render("./users/signin", {params: {login: "", key: ""}});
        await next();
    })
    .post('/signin', koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let userSignInModel = {};
                userSignInModel.login = validator.validateLogin(body.login);
                userSignInModel.key = validator.validateHex(body.key, "password");
                ctx.state.body = userSignInModel;
                await next();
            } catch(e) {
                ctx.status = 400;
                if (e instanceof ValidationError)
                    await ctx.render("./users/signin", {error: e.message, params: ctx.request.body});
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            await passport.authenticate('local', async(err, body) => {
                if(!body){
                    ctx.response.status = 403;
                    await ctx.render("./users/signin", { error: "Incorrect login or password", params: ctx.request.body });
                } else {
                    var key = body.key;
                    let curveJsonStr = curve.toJSONwithKey(key);
                    let curveJsonB64 = Buffer.from(curveJsonStr).toString("base64");
                    ctx.cookies.set('session', curveJsonB64);
                    await user.addVisit(body.user, body.note);
                    await ctx.login(body.user);
                    await ctx.redirect('/');
                    await next();
                }
            })(ctx);
        })
    .get('/signup', async (ctx, next) => {
        await ctx.render("./users/signup", {params: {login: ""}});
        await next();
    })
    .post('/signup', koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            try {
                let userSignUpModel = {};
                userSignUpModel.login = validator.validateLogin(body.login);
                ctx.state.body = userSignUpModel;
                await next();
            } catch(e) {
                if (e instanceof ValidationError) {
                    ctx.response.status = 400;
                    await ctx.render("./users/signup", {error: e.message, params: body});
                }
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            let body = ctx.state.body;
            if (await user.isExist(body.login)) {
                ctx.response.status = 400;
                await ctx.render("./users/signup", {error: "This user already exists", params: ctx.request.body});
            }
            else
                await next();
        },
        async (ctx, next) => {
            let body = ctx.state.body;
            let keys = curve.generateKeys();
            let userModel = await user.signup(body.login, keys[1]);
            let curveJsonStr = curve.toJSONwithKey(keys[0].toString(16));
            let curveJsonB64 = Buffer.from(curveJsonStr).toString("base64");
            ctx.cookies.set('session', curveJsonB64);
            await ctx.login(userModel);
            await ctx.render("./users/signup", {error: "Your password: " + keys[0].toString(16), params: ctx.request.body});
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
                    ctx.response.status = 400;
                else
                    throw e;
            }
        },
        async (ctx, next) => {
            book.addTag(ctx.state.user.id, ctx.state.body.bookId, ctx.state.body.tag);
            ctx.response.status = 200;
            await next();
        })
    .get('/journal',
        async (ctx, next) => {
            if (!ctx.isAuthenticated())
                ctx.response.status = 403;
            else
                await next();
        },
        async (ctx, next) => {
            let visits = await user.getLastUsers();
            visits = visits.map((e, i) => {return {login: e.login, note: e.note, date: e.date, index: i + 1}});
            await ctx.render("./users/journal", {visits: visits});
            await next();
        });

exports.routes = () => { return router.routes() };
exports.allowedMethods = () => { return router.allowedMethods() };