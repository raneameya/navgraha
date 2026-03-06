from shiny import ui

def input_time(id: str, label: str, value: str = '12:00', step: int = 1):
    '''
    Create a time input using the HTML5 <input type='time'> element.

    Args:
        id (str): Input id used to access the value in server logic.
        label (str): Display label.
        value (str): Default time value in HH:MM or HH:MM:SS format.
        step (int): Step size in seconds (1 enables seconds selection).
    
    Returns:
        A timeinput ui
    '''
    return ui.div(
        ui.tags.label(label, **{'for': id}),
        ui.tags.input(
            id = id,
            type = 'time',
            value = value,
            step = step,
            # time-input class id used in js to bind the input value so 
            # that it can be used server side.
            # form-control ensures visual consistency with other inputs
            class_ = 'time-input form-control'
        )
    )
