$(document).ready(function() {
    var inputs = [$("#x")[0], $("#y")[0], $("#z")[0]]
    inputs.forEach((e, i) => {
        e.oninput = function (event) {
            e.value = e.value.replace(/[^0-9-]/, "");
            e.value = e.value.replace(/([0-9-])-/, "$1");
        }
    });
});