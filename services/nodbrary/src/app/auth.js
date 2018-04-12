const passport = require('koa-passport');
const User = require('./models/user');
const Strategy = require('passport-local').Strategy;
const superEC = require('../app/super-ec');
let curve = new superEC();

passport.use(new Strategy({
        usernameField: 'login',
        passwordField: 'pass'
    },
    async (login, password, done) => {
        let user;
        try {
            user = await User.findOne({login: login}).exec();
            if (!user) {
                return done(null, false);
            }
            let sign = curve.sign(msg, password);
            let x = new BN(user.keyX);
            let y = new BN(user.keyY);
            let pubKey = curve.curve.point((x, y));
            if (!curve.verify(msg, pubKey, sign)) {
                return done(null, false);
            }
            return done(null, user);
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