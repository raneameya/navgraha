def divisional_map(divisional: str, type: str) -> str:
    if divisional == 'rasi':
        return 'rasi'
    elif divisional == 'navamsa':
        return 'navamsa'
    elif divisional == 'hora':
        return 'hora'
    elif divisional == 'dasamsa':
        if type == 'Traditional Parashari':
            return 'dasamsa_trd'
        elif type == 'Parashari reversed':
            return 'dasamsa_rev'
        elif type == 'Parashari reversed (6-9)':
            return 'dasamsa_rev69'
    elif divisional == 'vimsamsa':
        if type == 'Traditional Parashari':
            return 'vimsamsa_trd'
        elif type == 'Parashari reversed':
            return 'vimsamsa_rev'
    elif divisional == 'sastyamsa':
        if type == 'Traditional Parashari':
            return 'sastyamsa_trd'
        elif type == 'Parashari reversed':
            return 'sastyamsa_rev'
