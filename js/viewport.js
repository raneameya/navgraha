var width = 0;
var height = 0;
$(document).on("shiny:connected", function() {
    width = window.innerWidth;
    height = window.innerHeight;
    Shiny.onInputChange("width", width);
    Shiny.onInputChange("height", height);
});
$(window).resize(function() {
    width = window.innerWidth;
    height = window.innerHeight;
    Shiny.onInputChange("width", width);
    Shiny.onInputChange("height", height);
});