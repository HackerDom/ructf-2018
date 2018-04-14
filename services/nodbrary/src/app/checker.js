const randomstring = require('randomstring');
const Sentencer = require('sentencer');
const superEC = require('../app/super-ec');
let curve = new superEC();

function check_creds(user, password) {
    let verb = randomstring.generate({charset: 'alphabetic', length: 12}).toLowerCase();
    let note = Sentencer.make(user.login + " " + verb + " {{ an_adjective }} {{ noun }}");
    let sign = curve.sign(note, password);
    let publicPoint = curve.point(user.keyX, user.keyY);
    if (!curve.verify(note, publicPoint, sign))
        return false;
    return {user:user, key:password, note:note, sign:sign};
}

exports.check_creds = check_creds;