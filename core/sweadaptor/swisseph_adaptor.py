from dataclasses import dataclass
from datetime import timedelta

from core.misc.birth_event import BirthEvent

@dataclass
class SwissEphAdaptor:
    base_path: str
    binary: str
    birth: BirthEvent
    ayanamsa: str
    house: str
    output_cols: str
    ephemeris_path: str
    num_rows: int = 0
    time_delta: str = None
    planet_of_interest: list[str] | str = 'p'
    planet_to_difference: str = '0'

    def __post_init__(self):
        # Point to where ephemeris files live. This isn't a 
        # function because it is univerally required in all calls
        self.ephemeris_path_arg = {
            'ephemeris_path': f'-edir{self.base_path}{self.ephemeris_path}'
        }

    def birth_moment_args(self, offset_days:int = 0) -> dict:
        utc = self.birth.utc_datetime()
        if offset_days:
            utc = utc + timedelta(days = offset_days)
        return {
            'birth_date': f'-b{utc:%d.%m.%Y}',
            'birth_time': f'-utc{utc:%H:%M:%S}'
        }

    def birth_place_args(self) -> dict:
        # lat lon
        ll = (
            f'{str(self.birth.longitude)},'
            f'{str(self.birth.latitude)},'
        )
        geopos_arg = f'-geopos{ll}{self.birth.z_height}'
        house_arg = f'-house{ll}{self.house}'
        return {
            'geopos': geopos_arg,
            'house': house_arg
        }

    def ayanamsa_arg(self):
        ayanamsas = {
            'Fagan/Bradley':'00',
            'Lahiri':'1',
            'De Luce':'2',
            'Raman':'3',
            'Usha/Shashi':'4',
            'Krishnamurti':'5',
            'Djwhal Khul':'6',
            'Yukteshwar':'7',
            'J.N. Bhasin':'8',
            'Babylonian/Kugler 1':'9',
            'Babylonian/Kugler 2':'10',
            'Babylonian/Kugler 3':'11',
            'Babylonian/Huber':'12',
            'Babylonian/Eta Piscium':'13',
            'Babylonian/Aldebaran = 15 Tau':'14',
            'Hipparchos':'15',
            'Sassanian':'16',
            'Galact. Center = 0 Sag':'17',
            'J2000':'18',
            'J1900':'19',
            'B1950':'20',
            'Suryasiddhanta':'21',
            'Suryasiddhanta (mean Sun)':'22',
            'Aryabhata':'23',
            'Aryabhata (mean Sun)':'24',
            'SS Revati':'25',
            'SS Citra':'26',
            'True Citra':'27',
            'True Revati':'28',
            'True Pushya (PVRN Rao)':'29',
            'Galactic (Gil Brand)':'30',
            'Galactic Equator (IAU1958)':'31',
            'Galactic Equator':'32',
            'Galactic Equator mid-Mula':'33',
            'Skydram (Mardyks)':'34',
            'True Mula (Chandra Hari)':'35',
            'Dhruva/Gal.Center/Mula (Wilhelm)':'36',
            'Aryabhata 522':'37',
            'Babylonian/Britton':'38',
            'Vedic/Sheoran':'39',
            'Cochrane (Gal.Center = 0 Cap)':'40',
            'Galactic Equator (Fiorenza)':'41',
            'Vettius Valens':'42',
            'Lahiri 1940':'43',
            'Lahiri VP285 (1980)':'44',
            'Krishnamurti VP291':'45',
            'Lahiri ICRC':'46',
            'Tropical':''
        }
        out = (
            '' if self.ayanamsa == 'Tropical' 
            else f'-sid{ayanamsas[self.ayanamsa]}'
        )
        return {'ayanamsa': out}

    def output_cols_arg(self):
        return {'output_cols': f'-f{self.output_cols}'}

    def no_header_arg(self):
        return {'no_header_info': '-head'}
    
    def num_row_arg(self):
        return {'num_rows': f'-n{self.num_rows}'}
    
    def time_delta_arg(self):
        return {'time_delta_arg': f'-s{self.time_delta}'}
    
    def planet_args(self, planet_type:str):
        planet_mapping = {
            'Sun': '0',
            'Moon': '1',
            'Mercury': '2',
            'Venus': '3',
            'Mars': '4',
            'Jupiter': '5',
            'Saturn': '6',
            'Uranus': '7',
            'Neptune': '8',
            'Pluto': '9',
            'North node (mean)': 'm',
            'North node (true)': 't',
            'Lunar apogee (mean) (mean Lilith)': 'A',
            'Lunar apogee (osculating) (osc. Lilith)': 'B',
            'Lunar apogee (intp.) (intp. Lilith)': 'c',
            'Lunar perigee (intp.)': 'g',
            'Earth': 'C',
            'Ceres': 'F',
            'Chiron': 'D',
            'Pholus': 'E',
            'Pallas': 'G',
            'Juno': 'H',
            'Vesta': 'I',
            'Cupido': 'J',
            'Hades': 'K',
            'Zeus': 'L',
            'Kronos': 'M',
            'Apollon': 'N',
            'Admetos': 'O',
            'Vulkaunus': 'P',
            'Poseidon': 'Q',
            'Isis (Sevin)': 'R',
            'Nibiru (Sitchin)': 'S',
            'Harrington': 'T',
            'Leverrier\'s Neptune': 'U',
            'Adams\' Neptune': 'V',
            'Lowell\'s Pluto': 'W',
            'Pickering\'s Pluto': 'X',
            'Vulcan': 'Y',
            'White moon': 'Z',
            'Waldemath\'s dark Moon': 'w'
        }
        planet_group_mapping = {
            'd': '0123456789mtABCcg',
            'p': '0123456789mtABCcgDEFGHI'
        }
        p_arg = {
            'poi': self.planet_of_interest, 
            'pod': self.planet_to_difference
        }[planet_type]
        p_flag = {'poi': '-p', 'pod': '-d'}[planet_type]
        if isinstance(p_arg, str):
            try:
                out = (planet_mapping | planet_group_mapping)[p_arg]
            except KeyError:
                print(f'Planet code {p_arg} not found.')
        elif isinstance(p_arg, list):
            out = [planet_group_mapping[p] for p in p_arg]
            if not out:
                raise ValueError(f'None of the planet arguments were valid.')
            else:
                out = ''.join(out)
        return {f'planets_{planet_type}': f'{p_flag}{out}'}
