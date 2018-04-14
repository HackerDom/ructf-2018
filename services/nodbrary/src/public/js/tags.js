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
            $("#tag_input").removeClass("red-input");
            var tag = event.target.value;
            if (!tag.match(/^[a-z0-9,.()\-"!?;:'= ]*$/i))
                $("#tag_input").addClass("red-input");
            else
            {
                addTag(tag);
                $(".tags").removeClass("show");
                $(".dropdown-menu").removeClass("show");
            }
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
