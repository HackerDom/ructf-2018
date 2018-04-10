'use strict';

let validator = {
    validateNumber: str => {
        let number = Number.parseInt(str);
        return number === Number.NaN ? null : number;
    },
    validateString: str => {
        return str && str.match(/^[a-z]*$/i) ? str : null;
    },
    validatePassString: str => {
        return str && str.match(/^[a-z0-9]*$/i) && str.length > 8 ? str : null;
    }
};

exports.validator = validator;