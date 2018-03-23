function submitRegForm() {
    var loginIsValid = false;
    if (validateLogin())
        loginIsValid = checkLoginExisting();
    var passwordIsValid = validatePassword();
    return passwordIsValid && loginIsValid;
}

function submitLoginForm() {
    var loginIsValid = validateLogin();
    var passwordIsValid = validatePassword();
    if (loginIsValid && passwordIsValid)
    return validatePair();
}

function isUsernameFree() {
    var result = false;
    $.ajaxSetup({async: false});
    $.get("/exist/" + $('#username-field').val(), function(data, status) {
        result = !(data == "true" && status == "success");
    });
    return result;
}

function isValidPair(login, password) {
    var result = false;
    var passwordBase = window.btoa(encodeURI($('#pwd').val())).replace('/', '-');
    $.ajaxSetup({async: false});
    $.get("/isvalidpair/" + $('#username-field').val() + "/" + passwordBase, function(data, status) {
        result = (data == "true" && status == "success");
    });
    return result;
}

function validateField(inputField, errorMessage, validationFunc) {
    var valid = true;
    var input = $(inputField),
        val = input.val(),
        formGroup = input.parents('.form-group'),
        label = formGroup.find('label').text().toLowerCase(),
        fieldIcon = $('#' + label + '-field-icon');
    // console.log(regexp);
    // console.log(val);
    // console.log('test result:');
    // console.log(regexp.test(val));
    var res = !validationFunc(val);
    console.log(res);
   if (res) {
       console.log("Validation fail with " + val);
       formGroup.addClass('has-error').removeClass('has-success');
       fieldIcon.addClass('glyphicon-remove').removeClass('glyphicon-ok');
       input.tooltip({
           trigger: 'manual',
           placement: 'right',
           title: errorMessage
       }).tooltip('show');
       valid = false;
       console.log('field ' + ': FAIL');
   } else {
       formGroup.addClass('has-success').removeClass('has-error');
       fieldIcon.addClass('glyphicon-ok').removeClass('glyphicon-remove');
       console.log('field ' + ': OK');
       $('#username-icon').removeClass('glyphicon-remove');
   }
   return valid;
}

function validateLogin() {
    return validateField(
        '#username-field',
        'Login must satisfy regexp ^[a-z0-9_-]{4,16}$.',
        function (val) {
            return /^[a-z0-9_-]{4,16}$/.test(val)
        });
}

function validatePassword() {
    return validateField(
        '#pwd',
        'Password length must be between 1 and 20.',
        function (val) {
            return /^.{1,20}$/.test(val)
        });
}

function checkLoginExisting() {
    return validateField(
        '#username-field',
        'Login is already exist.',
        isUsernameFree
    );
}

function validatePair() {
    return validateField(
        '#pwd',
        'Password isn\'t correct.',
        function (passwordVal) {
            var loginVal = $('#username-field').val();
            return isValidPair(loginVal, passwordVal);
        }
    )
}

function removeError() {
    var input = $(this),
        formGroup = input.parents('.form-group'),
        label = formGroup.find('label').text().toLowerCase();
    input.tooltip('destroy').parents('.form-group').removeClass('has-error');
    $('#' + label + '-field-icon').removeClass('glyphicon-remove');
}

window.onload = function() {
    var regForm = $('#reg-form');
    var loginForm = $('#login-form');
    regForm.on('submit', submitRegForm);
    regForm.on('keydown', 'input', removeError);
    loginForm.on('submit', submitLoginForm);
    loginForm.on('keydown', 'input', removeError);
};
