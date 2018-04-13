'use strict';

$(document).ready(function() {
    $("#already_read").click(event => {
        addTag("already read");
    });

    $("#want_to_read").click(event => {
        addTag("want to read");
    });

    $("#tag_input").keyup(function(event) {
        if(event.keyCode==13) {
            addTag(event.target.value);
            $(".tags").removeClass("show");
            $(".dropdown-menu").removeClass("show");
            event.target.value = "";
        }
    });
});

function addTag(tag) {
    var tagElement = document.createElement("span");
    tagElement.setAttribute("class", "badge badge-pill badge-info");
    tagElement.innerHTML = tag;
    $(".tags").append(tagElement);
    var bookId = document.URL.toString().match(/\/book\/(\d+)/i)[1];

    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"bookId": bookId, "tag": tag}),
        url: "/tag",
    });
}
