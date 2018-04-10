'use strict';

const Router = require('koa-router');
const KoaBody = require('koa-body');
const convert = require('koa-convert');
let router = new Router();
let koaBody = convert(KoaBody());
let catalog = require('../app/catalog').routes;
let book = require('../app/book').routes;

router
    .get(['/', '/home'], async (ctx, next) => {
        await catalog.catalog(ctx, next);
        await next();
    })
    .get('/book', async (ctx, next) => {
        if (!ctx.query.id)
            await ctx.render('./service/404', {});
        else
            await book.book(ctx, next);
        await next();
    })
    .get('/create', async (ctx, next) => {
        await ctx.render("./books/create");
        await next();
    })
    .post('/add', koaBody, async (ctx, next) => {
        let body = ctx.request.body;
        await book.add(ctx, body);
        await next();
    });

exports.routes = () => { return router.routes() };