from dataclasses import dataclass

import pandas as pd

from core.chart.chart import chart
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor
from core.sweadaptor.swisseph_reader import SwissEphReader
from core.chart.chart_helpers import graha_nakshatra_traversal, sun_rise_set

@dataclass
class Panchanga:
    birth_chart: chart

    def df(self):
        tithi_and_karana = self.tithi_and_karana()
        tithi = tithi_and_karana['tithi']
        vara = self.vara()
        nakshatra = self.nakshatra()
        yoga = self.yoga()
        karana = tithi_and_karana['karana']
        panchanga = pd.DataFrame([
            {'Aṅga': 'Tithi'} | tithi,
            {'Aṅga': 'Vāra'} | vara,
            {'Aṅga': 'Nakṣatra'} | nakshatra,
            {'Aṅga': 'Yoga'} | yoga,
            {'Aṅga': 'Karaṇa'} | karana
        ])
        panchanga['% remaining'] = panchanga['% remaining'].apply(
            lambda x: str(round(100 * x, 2)) + '%'
        )
        return panchanga[['Aṅga', 'Name', 'Lord', '% remaining']]

    def tithi_and_karana(self):
        tithis = {
            1: {'Name':'Śukla Pratipadā', 'Lord': 'Sūrya'},
            2: {'Name':'Śukla Dvitīyā', 'Lord': 'Candra'},
            3: {'Name':'Śukla Tṛtīyā', 'Lord': 'Maṅgala'},
            4: {'Name':'Śukla Caturthī', 'Lord': 'Budha'},
            5: {'Name':'Śukla Pañcamī', 'Lord': 'Guru'},
            6: {'Name':'Śukla Ṣaṣṭhī', 'Lord': 'Śukra'},
            7: {'Name':'Śukla Saptamī', 'Lord': 'Śani'},
            8: {'Name':'Śukla Aṣṭamī', 'Lord': 'Rahu'},
            9: {'Name':'Śukla Navamī', 'Lord': 'Sūrya'},
            10: {'Name':'Śukla Daśamī', 'Lord': 'Candra'},
            11: {'Name':'Śukla Ekādaśī', 'Lord': 'Maṅgala'},
            12: {'Name':'Śukla Dvādaśī', 'Lord': 'Budha'},
            13: {'Name':'Śukla Trayodaśī', 'Lord': 'Guru'},
            14: {'Name':'Śukla Caturdaśī', 'Lord': 'Śukra'},
            15: {'Name':'Śukla Pūrṇimā', 'Lord': 'Śani'},
            16: {'Name':'Kṛṣṇa Pratipadā', 'Lord': 'Sūrya'},
            17: {'Name':'Kṛṣṇa Dvitīyā', 'Lord': 'Candra'},
            18: {'Name':'Kṛṣṇa Tṛtīyā', 'Lord': 'Maṅgala'},
            19: {'Name':'Kṛṣṇa Caturthī', 'Lord': 'Budha'},
            20: {'Name':'Kṛṣṇa Pañcamī', 'Lord': 'Guru'},
            21: {'Name':'Kṛṣṇa Ṣaṣṭhī', 'Lord': 'Śukra'},
            22: {'Name':'Kṛṣṇa Saptamī', 'Lord': 'Śani'},
            23: {'Name':'Kṛṣṇa Aṣṭamī', 'Lord': 'Rahu'},
            24: {'Name':'Kṛṣṇa Navamī', 'Lord': 'Sūrya'},
            25: {'Name':'Kṛṣṇa Daśamī', 'Lord': 'Candra'},
            26: {'Name':'Kṛṣṇa Ekādaśī', 'Lord': 'Maṅgala'},
            27: {'Name':'Kṛṣṇa Dvādaśī', 'Lord': 'Budha'},
            28: {'Name':'Kṛṣṇa Trayodaśī', 'Lord': 'Guru'},
            29: {'Name':'Kṛṣṇa Caturdaśī', 'Lord': 'Śukra'},
            30: {'Name':'Kṛṣṇa Amāvāsyā', 'Lord': 'Rahu'}
        }
        karanas = [
            {'Name': 'Bava', 'Lord': 'Śukra', 'Diety': 'Indra', 'Type': 'Cāra'},
            {'Name': 'Bālava', 'Lord': 'Śani', 'Diety': 'Brahmā', 'Type': 'Cāra'},
            {'Name': 'Kaulava', 'Lord': 'Ravi', 'Diety': 'Mitra', 'Type': 'Cāra'},
            {'Name': 'Taitila', 'Lord': 'Guru', 'Diety': 'Aryamā', 'Type': 'Cāra'},
            {'Name': 'Garija', 'Lord': 'Kuja', 'Diety': 'Bhūmi', 'Type': 'Cāra'},
            {'Name': 'Vaṇija', 'Lord': 'Śukra', 'Diety': 'Lakṣmī', 'Type': 'Cāra'},
            {'Name': 'Viṣṭi (Bhadrā)', 'Lord': 'Śani', 'Diety': 'Yama', 'Type': 'Cāra'},
            {'Name': 'Śakuni', 'Lord': 'Śukra', 'Diety': 'Kālī', 'Type': 'Sthira'},
            {'Name': 'Catuṣpāda', 'Lord': 'Ravi', 'Diety': 'Rudra', 'Type': 'Sthira'},
            {'Name': 'Nāga', 'Lord': 'Budha', 'Diety': 'Phaṇī', 'Type': 'Sthira'},
            {'Name': 'Kiṃstughna', 'Lord': 'Śani', 'Diety': 'Vāyu', 'Type': 'Sthira'},
        ]
        karanas = {1: karanas[10]} | {
            (k + 2): v for k, v in enumerate(karanas[0:7] * 8)
        } | {
            58: karanas[7],
            59: karanas[8],
            60: karanas[9]
        }
        sr = SwissEphReader(se = SwissEphAdaptor(
            base_path = './swisseph-master/',
            binary = 'swetest', 
            birth_event = self.birth_chart.birth_event,
            ayanamsa = self.birth_chart.swisseph_adaptor.ayanamsa,
            house = 'W',
            output_cols = 'PTl',
            ephemeris_path = 'ephe',
            num_rows = 1, 
            planet_of_interest = 'Moon', 
            planet_to_difference = 'Sun'
        ))
        ang_diff = sr.graha1_graha2_rel_diff()['Angular difference'][0]
        ang_diff = ang_diff + 360 if ang_diff < 0 else ang_diff
        tithi_index = (ang_diff // 12) + 1
        remaining_tithi = 1 - ((ang_diff / 12) % 1)
        karana_index = (ang_diff // 6) + 1
        remaining_karana = 1 - ((ang_diff / 6) % 1)
        tithi = tithis[tithi_index] | {'% remaining': float(remaining_tithi)}
        karana = karanas[karana_index] | {'% remaining': float(remaining_karana)}
        return {'tithi': tithi} | {'karana': karana}

    def vara(self):
        birth = self.birth_chart.birth_event.dt
        sunrise, sunset, sunrise_next = sun_rise_set(
            birth_chart = self.birth_chart
        )
        varas = {
            'Sunday': {'Name': 'Ravivāsara', 'Lord': 'Sūrya'},
            'Monday': {'Name': 'Somavāsara', 'Lord': 'Candra'},
            'Tuesday': {'Name': 'Maṅgalavāsara', 'Lord': 'Maṅgala'},
            'Wednesday': {'Name': 'Budhavāsara', 'Lord': 'Budha'},
            'Thursday': {'Name': 'Bṛhaspativāsara', 'Lord': 'Guru'},
            'Friday': {'Name': 'Śukravāsara', 'Lord': 'Śukra'},
            'Saturday': {'Name': 'Śanivāsara', 'Lord': 'Śani'},
        }
        vedic_weekday = sunrise.strftime('%A')
        remaining = 1 - ((birth - sunrise) / (sunrise_next - sunrise))
        return varas[vedic_weekday] | {
            '% remaining': float(remaining), 
            'sun_rise_time': sunrise
        }

    def nakshatra(self):
        nakshatra, lord, remaining = graha_nakshatra_traversal(
            birth_chart = self.birth_chart,
            graha = 'Candra', divisional = 'rasi'
        )
        return {
            'Name': nakshatra, 
            'Lord': lord, 
            '% remaining': float(remaining)
        }

    def yoga(self):
        yogas = {
            1: {'Name':'Viṣkumbha', 'Lord': 'Śani', 'Diety': 'Yama'},
            2: {'Name':'Prīti', 'Lord': 'Budha', 'Diety': 'Viṣṇu'},
            3: {'Name':'Āyuṣmān', 'Lord': 'Ketu', 'Diety': 'Candra'},
            4: {'Name':'Saubhāgya', 'Lord': 'Śukra', 'Diety': 'Brahmā'},
            5: {'Name':'Śobhana', 'Lord': 'Sūrya', 'Diety': 'Bṛhaspati'},
            6: {'Name':'Atigaṇḍa', 'Lord': 'Candra', 'Diety': 'Candra'},
            7: {'Name':'Sukarma', 'Lord': 'Maṅgala', 'Diety': 'Indra'},
            8: {'Name':'Dhṛti', 'Lord': 'Rāhu', 'Diety': 'Jala'},
            9: {'Name':'Śūla', 'Lord': 'Guru', 'Diety': 'Nāga'},
            10: {'Name':'Gaṇḍa', 'Lord': 'Śani', 'Diety': 'Agni'},
            11: {'Name':'Vṛddhi', 'Lord': 'Budha', 'Diety': 'Sūrya'},
            12: {'Name':'Dhruva', 'Lord': 'Ketu', 'Diety': 'Bhūmi'},
            13: {'Name':'Vyāghāta', 'Lord': 'Śukra', 'Diety': 'Pavana'},
            14: {'Name':'Harṣaṇa', 'Lord': 'Sūrya', 'Diety': 'Bhaga'},
            15: {'Name':'Vajra', 'Lord': 'Candra', 'Diety': 'Varuṇa'},
            16: {'Name':'Siddhi', 'Lord': 'Maṅgala', 'Diety': 'Gaṇeśa'},
            17: {'Name':'Vyatīpāta', 'Lord': 'Rāhu', 'Diety': 'Rudra'},
            18: {'Name':'Varīyān', 'Lord': 'Guru', 'Diety': 'Kubera'},
            19: {'Name':'Parigha', 'Lord': 'Śani', 'Diety': 'Viśvakarmā'},
            20: {'Name':'Śiva', 'Lord': 'Budha', 'Diety': 'Mitra'},
            21: {'Name':'Siddha', 'Lord': 'Ketu', 'Diety': 'Kārttikeya'},
            22: {'Name':'Sādhya', 'Lord': 'Śukra', 'Diety': 'Sāvitrī'},
            23: {'Name':'Śubha', 'Lord': 'Sūrya', 'Diety': 'Lakṣmī'},
            24: {'Name':'Śukla', 'Lord': 'Candra', 'Diety': 'Pārvatī'},
            25: {'Name':'Brahma', 'Lord': 'Maṅgala', 'Diety': 'Aśvinī Kumāras'},
            26: {'Name':'Indra', 'Lord': 'Rāhu', 'Diety': 'Pitṛs'},
            27: {'Name':'Vaidhṛti', 'Lord': 'Guru', 'Diety': 'Diti'}
        }
        placements = self.birth_chart.divisionals.rasi.placements
        sun_moon_lon_sum = sum(
            placements[placements['Graha'].isin(['Sūrya', 'Candra'])]['Lon']
        )
        sun_moon_lon_sum = sun_moon_lon_sum % 360
        yoga_index = (sun_moon_lon_sum // (360/27)) + 1
        remaining = 1 - ((sun_moon_lon_sum / (360/27)) % 1)
        return yogas[yoga_index] | {'% remaining': remaining}
