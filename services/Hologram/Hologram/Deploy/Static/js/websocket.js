$(document).ready(function() {
    var socket1 = null;

    var inputs = [$("#x")[0], $("#y")[0], $("#z")[0], $("#rad")[0]]
    inputs.forEach((e, i) => {
        e.oninput = function (event) {
            e.value = e.value.replace(/[^0-9-]/, "");
            e.value = e.value.replace(/([0-9-])-/, "$1");
            if (i == 3) {
                e.value = e.value.replace(/([0-9]).*/, "$1");
            }
        }
    });

    $("#add-halogram-btn").click(event => {
        var x = $("#x")[0].value;
        var y = $("#y")[0].value;
        var z = $("#z")[0].value;
        var rad = $("#rad")[0].value;
        socket1 = createWebSocket(x, y, z, rad)
        $("#input-halogram-parameters").remove()
    });
});

function validate(x) {
    if (!Number.parseInt(x)) {

    }
}

function createWebSocket(x, y, z, rad) {
    var loc = window.location, new_uri;
    new_uri = "ws:";
    new_uri += "//" + loc.host;
    new_uri += "/ws/holograms";
    var socket = new WebSocket(new_uri + "?x="+x+"&y="+y+"&z="+z+"&rad="+rad);

    socket.onopen = function() {
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log('Connection closed successfully');
        } else {
            console.log('Disconnected '); // ex: server process has been killed
        }
        console.log('Code: ' + event.code + ' reason: ' + event.reason);
    };

    socket.onmessage = function(event) {
        var cardTemplate = $(".template").clone();
        var hologram = JSON.parse(event.data);
        var card = cardTemplate.children(".card");
        var cardBody = card.children(".card-body");
        var cardTitle = cardBody.children(".card-title")

        cardTitle.children(".card-title-text").text(hologram.name);
        cardBody.children(".card-text").text(hologram.body);
        var v = hologram.x + ":" + hologram.y + ":" + hologram.z;
        card.children(".card-footer").text(v);
        
        cardTemplate.removeAttr("hidden");
        cardTemplate.removeClass("template");

        var container = $(".row");
        container.append(cardTemplate);
    };

    socket.onerror = function(error) {
        alert("Ошибка " + error.message);
    };

    return socket;
}