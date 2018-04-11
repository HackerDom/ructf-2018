'use strict';

class ValidationError extends Error{}

let validator = {
    validateNumber: (str, obj) => {
        if (!str)
            throw new ValidationError("Не заполнено поле " + obj);
        let number = Number.parseInt(str);
        if (number === Number.NaN)
            throw new ValidationError("Поле " + obj + " должно быть числом");
        return number;
    },
    validateLogin: str => {
        if (!str)
            throw new ValidationError("Не заполнено поле логин");
        str = str.toLowerCase();
        if (!str.match(/^[a-z0-9]*$/i))
            throw new ValidationError("Поле логин может содержать только цифры и буквы латинского алфавита");
        return str;
    },
    validatePass: str => {
        if (!str)
            throw new ValidationError("Не заполнено поле пароль");
        if (!str.match(/^[a-z0-9]*$/i))
            throw new ValidationError("Поле пароль может содержать только цифры и буквы латинского алфавита");
        return str;
    },
    validateString: (str, obj) => {
        if (!str)
            throw new ValidationError("Не заполнено поле " + obj);
        if (!str.match(/^[a-z0-9,.()\-"!?;:' ]*$/i))
            throw new ValidationError("Поле " + obj + " может содержать только цифры, буквы латинского алфавита и символы ',', '.', '(', ')', '-', '\"', '!', '?', ';', ':', '''");
        return str;
    }
};

exports.validator = validator;
exports.ValidationError = ValidationError;