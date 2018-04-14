$(document).ready(function () {
    $('.btn-subscribe').click(function () {
        $('.modal.subscribe .form').form('clear');
        $('.modal.subscribe').modal('show');
    });

    $('.btn-create').click(function () {
        $('.modal.create .form').form('clear');
        $('.modal.create').modal('show');
    });

    $('.subscribe.form')
        .form({
            fields: {
                invite: 'regExp[/^\\d+:(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/]'
            },
            inline: true,
            on: 'blur'
        });


    $('.subscribe.modal')
        .modal({
            onApprove: async function () {
                let form = $('.subscribe.form');
                if (form.form('is valid')) {
                    let invite = form.form('get value', 'invite');
                    let [id, encodedKey] = invite.split(':');
                    let key = base64decode(encodedKey);
                    let channel = await view(id);
                    if (!channel) {
                        alert('Channel not found');
                        return;
                    }
                    localStorageUpdate('subscribed', [], subscribed => {
                        if (!subscribed.find(info => info.id === id))
                            subscribed.push({id, key, name: channel.name});
                        return subscribed;
                    });
                    location.reload();
                }
            }
        });

    $('.create.form')
        .form({
            fields: {
                name: ['minLength[3]', 'maxLength[20]'],
                password: ['minLength[8]', 'maxLength[16]']
            },
            inline: true,
            on: 'blur'
        });

    $('.create.modal')
        .modal({
            onApprove: async function () {
                let form = $('.create.form');
                if (form.form('is valid')) {
                    let params = form.form('get values');
                    let id = await add_channel(params.name, params.password);
                    if (!id) {
                        alert('Cannot create channel');
                        return;
                    }
                    let key = await get_key(id, params.password);
                    if (!key) {
                        alert('Cannot receive channel key');
                        return;
                    }
                    localStorageUpdate('maintained', [], maintained => {
                        maintained.push({id, key, name: params.name});
                        return maintained;
                    });
                    location.reload();
                }
            }
        });

    reload_channels();

    $('.channels .item').click(function () {
        let id = $(this).data('id');
        load_posts(id);
        $('.channels .item').removeClass('active');
        $(this).addClass('active');
        let ownerBlock = $('.owner-block');
        if ($(this).parents('.channels-maintained').length) {
            ownerBlock.show();
            ownerBlock.data('id', id);
        } else {
            ownerBlock.hide();
        }
    });

    $('.item .btn-remove').click(function () {
        let id = $(this).closest('.item').data('id');
        let collectionName = $(this).data('collection');
        localStorageUpdate(collectionName, [], collection => collection.filter(info => info.id !== id));
        location.reload();
    });

    $('.add-post.form')
        .form({
            fields: {
                text: 'empty',
                password: ['minLength[8]', 'maxLength[16]']
            },
            inline: true,
            on: 'blur'
        })
        .submit(async function (e) {
            e.preventDefault();
            if (!$(this).form('is valid'))
                return;
            let id = $(this).data('id');
            let params = $(this).form('get values');
            if (await add_post(id, params.password, params.text))
                location.reload();
            else
                alert('Cannot add post');
        });

    $('.btn-addPost').click(function () {
        $('.add-post.form').submit();
    });

    $('.btn-invite').click(function () {
        let id = $(this).closest('.owner-block').data('id');
        let channel_info = localStorageGet('maintained').find(info => info.id === id);
        let encodedKey = base64encode(restoreArray(channel_info.key));
        $('.invite-text').text(`${channel_info.id}:${encodedKey}`);
        $('.modal.invite').modal('show');
    });

    $('.change-password.form')
        .form({
            fields: {
                password: ['minLength[8]', 'maxLength[16]'],
                new_password: ['minLength[8]', 'maxLength[16]']
            },
            inline: true,
            on: 'blur'
        });

    $('.change-password.modal')
        .modal({
            onApprove: async function () {
                let form = $('.change-password.form');
                if (form.form('is valid')) {
                    let id = form.data('id');
                    let params = form.form('get values');
                    if (await change_password(id, params.password, params.new_password)) {
                        alert('Password successfully changed');
                        location.reload();
                    } else {
                        alert('Password changing failed');
                    }
                }
            }
        });

    $('.btn-changePassword').click(function () {
        let id = $(this).closest('.owner-block').data('id');
        $('.change-password.form').data('id', id);
        $('.modal.change-password .form').form('clear');
        $('.modal.change-password').modal('show');
    });
});

function append_channels(container, channels) {
    for (let channel of channels) {
        let item = $('<a class="item"></a>');
        container.append(item);
        $(item).text(channel.name);
        $(item).append('<i class="icon link trash alternate outline btn-remove"></i>');
        $(item).data('id', channel.id);
    }
}

function reloadCollection(name) {
    let collection = localStorageGet(name) || [];
    let container = $(`.channels-${name} .channels-list`);
    append_channels(container, collection);
    container.find('.btn-remove').data('collection', name);
}

function reload_channels() {
    reloadCollection('subscribed');
    reloadCollection('maintained');
}

async function load_posts(channel_id) {
    let container = $('.posts-list');
    container.empty();
    let channel_infos = localStorageGet('subscribed') || [];
    channel_infos = channel_infos.concat(localStorageGet('maintained') || []);
    let channel_info = channel_infos.find(info => info.id === channel_id);
    if (!channel_info)
        return;
    let channel = await view(channel_id);
    channel.decrypt(restoreArray(channel_info.key));
    for (let post of channel.posts) {
        let item = $('<div class="ui segment"><pre></pre></div>');
        container.append(item);
        $(item).children('pre').text(post);
    }
}

function add_channel(name, password) {
    return fetch("/add_channel", postOptions({name, password}))
        .then(response => response.status === 201 ? response.text() : null)
        .then(text => text.split(':')[1]);
}

function add_post(channel_id, password, text) {
    return fetch(`/add_post?channel_id=${channel_id}`, postOptions({password, text}))
        .then(response => response.status === 201);
}

function get_key(channel_id, password) {
    return fetch(`/key?channel_id=${channel_id}`, postOptions({password}))
        .then(response => response.status === 200 ? response.arrayBuffer() : null)
        .then(buffer => new Uint8Array(buffer));
}

function change_password(channel_id, password, new_password) {
    return fetch(`/change_password?channel_id=${channel_id}`, postOptions({password, new_password}))
        .then(response => response.status === 200);
}

function view(channel_id) {
    return fetch(`/view?channel_id=${channel_id}`)
        .then(response => response.status === 200 ? response.arrayBuffer() : null)
        .then(buffer => new Channel(buffer));
}

class Channel {
    constructor(buffer) {
        this._buffer = buffer;
        this._dataview = new DataView(buffer);
        this._position = 0;
        this.name = this._read_str();
        this.posts = [];
        while (this._position < buffer.byteLength) {
            this.posts.push(this._read_buf());
        }
    }

    decrypt(key) {
        this.posts = this.posts.map(post => this._decrypt_post(post, key));
    }

    _decrypt_post(post, key) {
        let resultBytes = [];
        for (let i = 0; i < post.length; i++) {
            resultBytes[i] = post[i] ^ key[i % key.length];
        }
        return this._buf_to_str(new Uint8Array(resultBytes));
    }

    _read_long() {
        let result = this._dataview.getUint32(this._position, true);
        this._position += 8;
        return result;
    }

    _read_buf() {
        let size = this._read_long();
        let result = new Uint8Array(this._buffer, this._position, size);
        this._position += size;
        return result;
    }

    _read_str() {
        return this._buf_to_str(this._read_buf());
    }

    _buf_to_str(buf) {
        return new TextDecoder("ascii").decode(buf);
    }
}

function querystring(obj) {
    return Object.keys(obj).map(key => `${key}=${encodeURIComponent(obj[key])}`).join('&');
}

function postOptions(bodyData) {
    return {
        method: "POST",
        body: querystring(bodyData),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    };
}

function base64decode(base64) {
    let raw = atob(base64);
    let rawLength = raw.length;
    let array = new Uint8Array(new ArrayBuffer(rawLength));

    for (i = 0; i < rawLength; i++) {
        array[i] = raw.charCodeAt(i);
    }
    return array;
}

function base64encode(array) {
    return btoa(String.fromCharCode(...array));
}

function restoreArray(obj) {
    return new Uint8Array(Object.assign([], obj));
}

function localStorageUpdate(key, default_value, updater) {
    let current = JSON.parse(localStorage.getItem(key)) || default_value;
    localStorage.setItem(key, JSON.stringify(updater(current)));
}

function localStorageGet(key) {
    return JSON.parse(localStorage.getItem(key) || 'null');
}
