'use strict';

class ValidationError extends Error{}

let validator = {
    validateNumber: (str, obj) => {
        if (!str)
            throw new ValidationError("Field " + obj + "couldn't be empty");
        let number = Number.parseInt(str);
        if (number === Number.NaN)
            throw new ValidationError("Field " + obj + " should be a digit");
        return number;
    },
    validateLogin: str => {
        if (!str)
            throw new ValidationError("Field login couldn't be empty");
        if (!str.match(/^[a-zA-Z0-9]*$/i))
            throw new ValidationError("Field login should contain only letters, digits");
        return str;
    },
    validateString: (str, obj) => {
        if (!str)
            throw new ValidationError("Field " + obj + " couldn't be empty");
        if (!str.match(/^[a-zA-Z0-9,.()\-"!?;:'= ]*$/i))
            throw new ValidationError("Field  " + obj + " should contain only letters, digits or symbols: ',', '.', '(', ')', '-', '\"', '!', '?', ';', ':', ''', '='");
        return str;
    },
    validateHex: (str, obj) => {
        if (!str)
            throw new ValidationError("Field " + obj + "couldn't be empty");
        if (!str.match(/^[a-f0-9]*$/i))
            throw new ValidationError("Field " + obj + " should contain only hex-symbols");
        return str;
    }
};

exports.validator = validator;
exports.ValidationError = ValidationError;