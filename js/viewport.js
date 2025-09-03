var width = 0;
var height = 0;
$(document).on("shiny:connected", function() {
    width = window.innerWidth;
    height = window.innerHeight;
    Shiny.setInputValue("width", width);
    Shiny.setInputValue("height", height);
});
$(window).resize(function() {
    width = window.innerWidth;
    height = window.innerHeight;
    Shiny.setInputValue("width", width);
    Shiny.setInputValue("height", height);
});