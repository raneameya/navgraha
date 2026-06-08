var width = 0;
var height = 0;
var resizeTimeout;
$(document).on("shiny:connected", function() {
    width = window.innerWidth;
    height = window.innerHeight;
    Shiny.setInputValue("width", width);
    Shiny.setInputValue("height", height);
});
$(window).resize(function() {
// Clear the timeout if the window is still resizing
    clearTimeout(resizeTimeout);
    
    // Wait 250ms after the last resize event before telling Python
    resizeTimeout = setTimeout(function() {
        width = window.innerWidth;
        height = window.innerHeight;
        Shiny.setInputValue("width", width);
        Shiny.setInputValue("height", height);
    }, 250);
});
var TimeInputBinding = new Shiny.InputBinding();
$.extend(TimeInputBinding, {
    find: function(scope) {
        // Find all instances of our custom input class
        return $(scope).find(".time-input");
    },
    getValue: function(el) {
        // Get the value from the HTML element
        return $(el).val();
    },
    subscribe: function(el, callback) {
        // Subscribe to changes (e.g., "change" event)
        $(el).on("change.TimeInputBinding", function(event) {
            callback();
        });
    },
    unsubscribe: function(el) {
        $(el).off(".TimeInputBinding");
    }
});

// Register the binding
Shiny.inputBindings.register(TimeInputBinding);
