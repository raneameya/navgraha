def divisional_map(divisional: str, type: str) -> str:
    if divisional == 'rasi':
        return 'rasi'
    elif divisional == 'navamsa':
        return 'navamsa'
    elif divisional == 'hora':
        if type == 'Parashari':
            return 'hora_psr'
        elif type == 'Uma Shambhu':
            return 'hora_us'
        elif type == 'Parivṛtti':
            return 'hora_prv'
        elif type == 'Kāśīnāth':
            return 'hora_ksn'
        elif type == 'Jagannāth':
            return 'hora_jgn'
        elif type == 'Samasaptaka':
            return 'hora_ssp'
        elif type == 'Maṇḍūka':
            return 'hora_mdk'
        elif type == 'Lābha maṇḍūka':
            return 'hora_lmk'
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
    elif divisional == 'trimsamsa':
        if type == 'Parashari':
            return 'trimsamsa_psr'
        elif type == 'Parivṛtti':
            return 'trimsamsa_prv'
    elif divisional == 'khavedamsa':
        return 'khavedamsa'
    elif divisional == 'sastyamsa':
        if type == 'Parashari':
            return 'sastyamsa_psr'
        elif type == 'Parashari reversed':
            return 'sastyamsa_rev'
