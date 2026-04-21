def dasa_offset_text(offset_days):
    if offset_days > 0:
        direction = 'future'
    elif offset_days < 0:
        direction = 'past'
    else:
        direction = ''
    if abs(offset_days) > 0:
        dasa_shift_text = (
            f'Daśās shifted in the {direction} by '
            f'{abs(offset_days)} days'
        )
    else:
        dasa_shift_text = ''
    return dasa_shift_text
