'use strict';

const koa = require('koa');
const Pug = require('koa-pug');
const compose = require('koa-compose');
const config = require('config');
const path = require('path');

const app = new koa();

const pug = new Pug({
    viewPath: 'src/templates',
    debug: false,
    pretty: false,
    compileDebug: false,
    app: app
});

require('koa-locals')(app);

app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        console.log(err);
        await ctx.render('service/error', {
            message: err.message,
            error: err
        });
    }}
);

let mongoose = require('mongoose');

mongoose.Promise = Promise;
let mongoConnectionUrl = 'mongodb://' +
    config.get('mongo.user') + ':' +
    config.get('mongo.pass') + '@' +
    'localhost:27017/test';
mongoose.connect(mongoConnectionUrl);

app.use(async (ctx, next) => {
    const start = new Date();
    await next();
    const ms = new Date() - start;
    console.log(`${ctx.method} ${ctx.url} - ${ms}`);
});

pug.use(app);

var projectRoot = __dirname;
var staticRoot = path.join(projectRoot, '../public');
console.log(staticRoot);

var middlewareStack = [
    require('koa-session')(app),
    require('koa-static')(staticRoot),
];

app.use(compose(middlewareStack));
app.use(require('./handlers').routes());

app.listen(config.get('server.port'));