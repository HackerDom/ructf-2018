const passport = require('koa-passport');
const User = require('./models/user');
const Strategy = require('passport-local').Strategy;
const superEC = require('../app/super-ec');
const randomstring = require("randomstring");
let curve = new superEC();

passport.use(new Strategy({
        usernameField: 'login',
        passwordField: 'key'
    },
    async (login, password, done) => {
        let user;
        try {
            user = await User.findOne({login: login}).exec();
            if (!user) {
                return done(null, false);
            }
            let msg = "Hi!";
            let sign = curve.sign(msg, password);
            let publicPoint = curve.curve.point(user.keyX, user.keyY);
            if (!curve.verify(msg, publicPoint, sign)) {
                return done(null, false);
            }
            return done(null, {user:user, key:password});
        } catch(err) {
            return done(err, null);
        }
    }
));

passport.serializeUser((user, done) => { done(null, user.id); });

passport.deserializeUser(async (id, done) => {
    try {
        let user = await User.findOne({id: id}).exec();
        done(null, user);
    }
    catch(err)
    {
        done(err, null);
    }
});