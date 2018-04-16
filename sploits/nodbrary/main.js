const sha1 = require('sha1');
const BN = require('bn.js');

var n = new BN(617666383997);

function crypt(msg){
    return "0x"+new BN(sha1(msg)).umod(n).toString(16);
}


var msg1 = "User ntwkkkroauqx a shyer tanzania";
var msg2 = "User bnzaocvxugid a niggling airmail";

var msg_main = "JohnTucker xmqvihlsciqt a wanton gazelle";
console.log(crypt(msg1), crypt(msg2), crypt(msg_main));