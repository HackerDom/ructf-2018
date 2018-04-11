'use strict';

const Router = require('koa-router');
const KoaBody = require('koa-body');
const convert = require('koa-convert');
let router = new Router();
let koaBody = convert(KoaBody());
let catalog = require('../app/catalog').routes;
let book = require('../app/book').routes;
let user = require('../app/user').routes;
let validator = require('../app/inputValidator').validator;

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
        await ctx.render("./books/create");
        await next();
    })
    .post('/add', koaBody, async (ctx, next) => {
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
            if (!validator.validateString(body.login) ||
                !validator.validatePassString(body.pass)) {
                await ctx.render("./users/signin", {error: "Исправьте ошибки", params: body});
            }
            else
                await next();
        },
        async (ctx, next) => {
            let body = ctx.request.body;
            let userModel = await user.signin(body);
            if (userModel)
                await ctx.redirect("/");
            else
                await ctx.redirect("/signin");
            await next();
        })
    .get('/signup', async (ctx, next) => {
        await ctx.render("./users/signup", {params: {login: "", pass: "", passConfirm: ""}});
        await next();
    })
    .post('/signup', koaBody,
        async (ctx, next) => {
            let body = ctx.request.body;
            if (!validator.validateString(body.login) ||
                !validator.validatePassString(body.pass) ||
                !validator.validatePassString(body.passConfirm))
                await ctx.render("./users/signup", {error: "Исправьте ошибки", params: body});
            else
                await next();
        },
        async (ctx, next) => {
            let body = ctx.request.body;
            console.log(body.pass)
            console.log(body.passConfirm)

            if (body.pass != body.passConfirm)
                await ctx.render("./users/signup", {error: "Исправьте ошибки", params: body});
            else
                await next();
        },
        async (ctx, next) => {
            let body = ctx.request.body;
            await user.signup(body);
            await ctx.redirect("/");
            await next();
        });

exports.routes = () => { return router.routes() };
exports.allowedMethods = () => { return router.allowedMethods() };