const passport = require('koa-passport');
const User = require('./models/user');
const Strategy = require('passport-local').Strategy;
const superEC = require('../app/super-ec');
const Sentencer = require('sentencer');
const randomstring = require('randomstring');
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
            let verb = randomstring.generate({charset: 'alphabetic', length: 12}).toLowerCase();
            let note = Sentencer.make(user.login + " " + verb + " {{ an_adjective  }} {{ noun }}");
            let sign = curve.sign(note, password);
            let publicPoint = curve.curve.point(user.keyX, user.keyY);
            if (!curve.verify(note, publicPoint, sign)) {
                return done(null, false);
            }
            return done(null, {user:user, key:password, note:note});
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