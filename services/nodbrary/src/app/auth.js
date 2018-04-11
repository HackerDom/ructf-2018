const passport = require('koa-passport');
const User = require('./models/user');
const Strategy = require('passport-local').Strategy;

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
            if (user.pass != password) {
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