'use strict';

const BN = require('bn.js');
const elliptic = require('elliptic');
const sha1 = require('sha1');

function SuperEC() {
    this.curve = new elliptic.curve.short(
    {
        p: new BN(617665577873),
        a: new BN(22541923),
        b: new BN(27623856),
        g: [
            new BN(228638339943), 
            new BN(433622854135)
        ],
        n: new BN(617666383997)
    });
    this.k = new BN(361792168050);
}
module.exports = SuperEC;

SuperEC.prototype.generateKeys = function generateKeys() {
    var privKey = new BN(Math.floor(Math.random() * this.curve.p) + 1);
    var publicPoint = this.curve.g.mul(privKey);
    return [privKey, publicPoint];
}

SuperEC.prototype.sign = function sign(msg, privKey) {
    privKey = new BN(privKey, 16);
    var hashMsg = new BN(sha1(msg)).umod(this.curve.n);
    while (true) {
        if (typeof this.k === 'undefined') this._generateK();
        var P = this.curve.g.mul(this.k);
        if (P.isInfinity())
        {
            this._generateK();
            continue;
        }

        var r = P.getX().umod(this.curve.n);
        if (r.cmpn(0) === 0)
        {
            this._generateK();
            continue;
        }

        var s1 = this.k.invm(this.curve.n);
        var s2 = r.mul(privKey).iadd(hashMsg);
        var s = s1.mul(s2).umod(this.curve.n);
        if (s.cmpn(0) === 0)
        {
            this._generateK();
            continue;
        }

        return [r, s];
    }
}

SuperEC.prototype.verify = function verify(msg, publicPoint, signature) {
    var hashMsg = new BN(sha1(msg)).umod(this.curve.n);
    var r = signature[0];
    var s = signature[1];
    
    if (!this.curve.validate(publicPoint))
        return false;

    if (!publicPoint.mul(this.n).isInfinity())
        return false;
    
    if (r.cmpn(1) < 0 || r.cmp(this.curve.n) >= 0 || s.cmpn(1) < 0 || s.cmp(this.curve.n) >= 0)
        return false;

    var w = s.invm(this.curve.n);
    var u1 = w.mul(hashMsg).umod(this.curve.n);
    var u2 = w.mul(r).umod(this.curve.n);
    var a = this.curve.g.mul(u1);
    var b = publicPoint.mul(u2);

    return a.add(b).getX().umod(this.curve.n).cmp(r) === 0;
}

SuperEC.prototype._generateK = function _generateK() {
    this.k = new BN(Math.floor(Math.random() * this.curve.p) + 1);
    console.log('k:',this.k.toString(10), 'n:', this.curve.n.toString(10));
    return
}

