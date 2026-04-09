def divisional_map(divisional: str, type: str) -> str:
    if divisional == 'rasi':
        return 'rasi'
    elif divisional == 'navamsa':
        return 'navamsa'
    elif divisional == 'hora':
        return 'hora'
    elif divisional == 'chathurtamsa':
        if type == 'Parashari':
            return 'chathurtamsa_psr'
        elif type == 'Parivṛtti':
            return 'chathurtamsa_prv'
    elif divisional == 'dasamsa':
        if type == 'Parashari':
            return 'dasamsa_psr'
        elif type == 'Parashari reversed':
            return 'dasamsa_rev'
        elif type == 'Parashari reversed (6-9)':
            return 'dasamsa_rev69'
    elif divisional == 'vimsamsa':
        if type == 'Parashari':
            return 'vimsamsa_psr'
        elif type == 'Parashari reversed':
            return 'vimsamsa_rev'
    elif divisional == 'sastyamsa':
        if type == 'Parashari':
            return 'sastyamsa_psr'
        elif type == 'Parashari reversed':
            return 'sastyamsa_rev'
