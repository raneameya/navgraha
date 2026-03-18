from shiny import App, ui, render, req, reactive
from datetime import datetime, time
from zoneinfo import ZoneInfo
from core.data.constants import rnp, ayanamsas, yr_len
import core.misc.stdout_to_pd as std2pd
import core.misc.misc_functions as mf
import core.chart.chart as crt
from core.panchanga.panchanga import Panchanga
import core.dasas.vimsottari_dasa as vd
import core.tajaka.sol_cross as sc
from core.appui.icons import icon_gear
from core.appui.time_input import input_time
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor

dasa_sub_levels = {
    '0': 'Mahadaśā', '1': 'Antardaśā', '2': 'Pratyantardaśā',
    '3': 'Sookśmaantardaśā'#, '4': 'Praanaantardaśā', '5': 'Dehaantardaśā'
}
divisional_choices = {'rasi': 'Rāśi', 'navamsa': 'Navāmśā', 'hora': 'Horā'}

natal_chart_ui = ui.accordion_panel(
    'Chart',
    ui.output_plot(id = 'natal_plot')
)

natal_table_ui = ui.accordion_panel(
    'Table',
    ui.output_data_frame(id = 'natal_table')
)

natal_panchanga_ui = ui.accordion_panel(
    'Pañcāṅga',
    ui.output_data_frame(id = 'natal_panchanga')
)

natal_dasa_ui = ui.accordion_panel(
    'Daśa',
    ui.row(
        ui.input_numeric(
            id = 'dasa_offset_days',
            label = '# days to offset daśa (+ve/-ve)',
            value = 0, step = 1
        ),
        ui.input_select(
            id = 'vimsottari_dasa_sub_level',
            label = 'Daśā level',
            choices = dasa_sub_levels
        )
    ),
    ui.output_text(id = 'natal_dasa_offset_info'),
    ui.output_data_frame(id = 'natal_vimsottari_dasa_df')
)

natal_ui = ui.nav_panel(
    'Natal',
    ui.output_text(id = 'natal_info'),
    ui.input_select(
            id = 'natal_divisional',
            label = '',
            choices = divisional_choices
    ),
    ui.accordion(
        natal_chart_ui,
        natal_table_ui,
        natal_panchanga_ui,
        natal_dasa_ui
    )
)

tajaka_chart_ui = ui.accordion_panel(
    'Chart',
    ui.output_plot(id = 'tajaka_plot')
)

tajaka_table_ui = ui.accordion_panel(
    'Table',
    ui.output_data_frame(id = 'tajaka_table')
)

tajaka_panchanga_ui = ui.accordion_panel(
    'Pañcāṅga',
    ui.output_data_frame(id = 'tajaka_panchanga')
)

tajaka_dasa_ui = ui.accordion_panel(
    'Daśa',
    ui.row(
        ui.input_numeric(
            id = 'tajaka_dasa_offset_days',
            label = '# days to offset daśa (+ve/-ve)',
            value = 0, step = 1
        ),
        ui.input_select(
            id = 'tajaka_vimsottari_dasa_sub_level',
            label = 'Daśā level',
            choices = dasa_sub_levels
        )
    ),
    ui.output_text(id = 'tajaka_dasa_offset_info'),
    ui.output_data_frame(id = 'tajaka_vimsottari_dasa_df')
)

tajaka_ui = ui.nav_panel(
    'Tājaka',
    ui.output_text(id = 'tajaka_info'),
    ui.layout_column_wrap(
        ui.output_ui(id = 'tajaka_divisional_choices'),
        ui.output_ui(id = 'tajaka_year_choices')
    ),
    ui.accordion(
        tajaka_chart_ui,
        tajaka_table_ui,
        tajaka_panchanga_ui,
        tajaka_dasa_ui
    )
)

settings_ui = ui.nav_panel(
    '',
    ui.accordion(
        ui.accordion_panel(
            'Preferences', 
            ui.input_select(
                id = 'b_ayanamsa',
                label = 'Ayanāṁśa',
                choices = ayanamsas, 
                selected = 'True Pushya (PVRN Rao)'
            ),
            ui.input_select(
                id = 'chart_style',
                label = 'Chart style',
                choices = ['South Indian', 'North Indian']
            )
        ),
        ui.accordion_panel(
            'Constants'
        )
    ),
    icon = icon_gear
)

app_ui = ui.page_sidebar(
    # Sidebar needs to be open so that the birth inputs (e.g. date, time, 
    # ayanāṁśa) are initialised.
    ui.sidebar(
        ui.output_ui(id = 'birth_input'),
        title = 'Birth inputs', open = 'open', id = 'sidebar'
    ),
    ui.include_js(path = 'core/js/custom.js'),
    ui.navset_card_underline(
        natal_ui,
        tajaka_ui,
        ui.nav_spacer(),
        settings_ui,
        ui.nav_control(ui.input_dark_mode(id = 'dark_mode')),
        id = 'pill'
    )
)

def server(input, output, session):

    @reactive.effect
    def close_sidebar():
        # Close sidebar when app initially loads.
        ui.update_sidebar(id = 'sidebar', show = False)

    @render.data_frame
    @reactive.event(input.search_place)
    def filtered_places():
        # Filter file for only matches to entered birth place
        cmd = 'grep -i "' + input.b_place() + '" places.txt'
        # Column names as reference. Not used as explained below
        colnames = [
            'geonameid', 'name', 'asciiname', 'latitude', 'longitude',
            'country code', 'elevation', 'population', 'timezone'
        ]
        # Providing column names makes it ignore column names present in file
        places = std2pd.read_stdout(
            cmd = cmd, reader = 'csv', sep = '\t', col_names = colnames
        )
        places.sort_values(
            by = ['population'], ascending = False, inplace = True
        )
        return render.DataGrid(places, selection_mode = 'rows')

    @reactive.effect
    @reactive.event(input.search_place)
    def input_modal():
        # Modal containing places
        m = ui.modal(
            ui.output_data_frame(id = 'filtered_places'),
            title = 'Click on a place to confirm details',
            easy_close = True,
            size = 'xl'
        )
        ui.modal_show(m)

    # Update values in input fields based on place selection by user
    @reactive.effect
    def update_birth_data_selected():
        place_selected = filtered_places.data_view(selected = True)
        req(not place_selected.empty)
        lon = place_selected.longitude.iloc[0]
        lat = place_selected.latitude.iloc[0]
        place = place_selected.name.iloc[0]
        tz = place_selected.timezone.iloc[0]
        ui.update_numeric('b_lon', value = lon)
        ui.update_numeric('b_lat', value = lat)
        ui.update_text('b_tz', value = tz)
        ui.update_text('b_place', value = place)
        # Close the place search modal user clicks on row
        ui.modal_remove()
        # Close sidebar when user selects place
        ui.update_sidebar(id = 'sidebar', show = False)

    @reactive.calc
    def birth_event():
        # Default to today unless date is valid
        b_date = input.b_date() or datetime.today()
        # Get hr, min, sec from time input which is text
        b_hr, b_mi, b_sc = mf.parse_time(input.b_time())
        be = BirthEvent(
            dt = datetime.combine(
                date = b_date, 
                time = time(b_hr, b_mi, b_sc), 
                tzinfo = ZoneInfo(input.b_tz())
            ), 
            latitude = input.b_lat(), 
            longitude = input.b_lon(), 
            z_height = 0, 
            place = input.b_place()
        )
        return be

    @reactive.calc
    def swisseph_adaptor():
        se = SwissEphAdaptor(
            base_path = './swisseph-master/',
            binary = 'swetest', 
            birth_event = birth_event(),
            ayanamsa = input.b_ayanamsa(),
            house = 'W',
            output_cols = 'TPlLsBj',
            ephemeris_path = 'ephe'
        )
        return se

    @reactive.calc
    def natal_chart():
        '''
        Return a chart object that can be reused across the app
        '''
        return crt.chart(swisseph_adaptor = swisseph_adaptor())

    @reactive.calc
    def natal_divisional():
        return getattr(natal_chart().divisionals, input.natal_divisional())

    @render.plot
    def natal_plot():
        return natal_divisional().chart_plot(
            dark = input.dark_mode() == 'dark',
            style = input.chart_style(),
            title = divisional_choices[input.natal_divisional()]
        )

    @render.data_frame
    def natal_table():
        p = natal_divisional().display_table
        return p
    
    @render.data_frame
    def natal_panchanga():
        p = Panchanga(birth_chart = natal_chart())
        return p.df()

    @reactive.calc
    def natal_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = natal_chart(),
            divisional = input.natal_divisional(),
            sub_dasa_level = int(input.vimsottari_dasa_sub_level()),
            dasa_offset_days = input.dasa_offset_days(),
            trunc_intervals = True
        )

    @render.data_frame
    def natal_vimsottari_dasa_df():
        dasas = natal_vimsottari_dasa()
        # Adjust number below to increase/decrease table height
        return render.DataGrid(
            data = dasas.dasa_to_df(), height = f'{input.height() - 300}px',
            filters = int(input.vimsottari_dasa_sub_level()) > 0
        )

    @render.text
    def natal_info():
        # To give user feedback about birth place & time selection
        return str(birth_event())

    @render.text
    def natal_dasa_offset_info():
        dasa_offset_days = natal_vimsottari_dasa().dasa_offset_days
        if dasa_offset_days > 0:
            direction = 'future'
        elif dasa_offset_days < 0:
            direction = 'past'
        else:
            direction = ''
        if abs(dasa_offset_days) > 0:
            dasa_shift_text = (
                f'Daśās shifted in the {direction} by '
                f'{abs(dasa_offset_days)} days'
            )
        else:
            dasa_shift_text = ''
        return dasa_shift_text

    @reactive.calc
    def tajaka_chart():
        args = mf.chart_kwargs(
            chart = natal_chart(),
            dt = sc.sol_cross(
                yr = int(input.tajaka_year()),
                birth_crt = natal_chart(),
                tropical = True
            )
        )
        return crt.chart(**args)

    @reactive.calc
    def tajaka_divisional():
        return getattr(tajaka_chart().divisionals, input.tajaka_divisional())

    @render.plot
    def tajaka_plot():
        return tajaka_divisional().chart_plot(
            dark = (input.dark_mode() == 'dark'),
            style = input.chart_style(),
            title = divisional_choices[input.tajaka_divisional()]
        )

    @render.data_frame
    def tajaka_table():
        out = tajaka_divisional().display_table
        return out
 
    @render.data_frame
    def tajaka_panchanga():
        p = Panchanga(birth_chart = tajaka_chart())
        return p.df()

    @render.text
    def tajaka_info():
        return tajaka_chart().repr_str

    @reactive.calc
    def tajaka_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = tajaka_chart(),
            divisional = input.tajaka_divisional(),
            sub_dasa_level = int(input.tajaka_vimsottari_dasa_sub_level()),
            dasa_offset_days = input.tajaka_dasa_offset_days(),
            trunc_intervals = True,
            lifespan = 1
        )

    @render.text
    def tajaka_dasa_offset_info():
        dasa_offset_days = tajaka_vimsottari_dasa().dasa_offset_days
        if dasa_offset_days > 0:
            direction = 'future'
        elif dasa_offset_days < 0:
            direction = 'past'
        else:
            direction = ''
        if abs(dasa_offset_days) > 0:
            dasa_shift_text = (
                f'Daśās shifted in the {direction} by '
                f'{abs(dasa_offset_days)} days'
            )
        else:
            dasa_shift_text = ''
        return dasa_shift_text

    @render.data_frame
    def tajaka_vimsottari_dasa_df():
        dasas = tajaka_vimsottari_dasa()
        return render.DataGrid(
            data = dasas.dasa_to_df(),
            # Adjust number below to increase/decrease table height
            height = f'{input.height() - 300}px',
            filters = int(input.tajaka_vimsottari_dasa_sub_level()) > 0
        )

    @render.ui
    def birth_input():
        ui_out = ui.row(
            ui.input_date(
                id = 'b_date',
                label = 'Date',
                value = datetime.today().strftime('%Y-%m-%d'),
                format = 'yyyy-mm-dd',
                weekstart = 0,
                autoclose = True
            ),
            input_time(
                id = 'b_time',
                label = 'Time',
                value = datetime.now().strftime('%H:%M:%S'),
                step = 1
            ),
            ui.input_text(
                id = 'b_place',
                label = 'Place',
                value = 'Auckland'
            ),
            ui.input_numeric(
                id = 'b_lon',
                label = 'Longitude',
                value = 174.74304,
                min = -180,
                max = 180
            ),
            ui.input_numeric(
                id = 'b_lat',
                label = 'Latitude',
                value = -36.85582,
                min = -90,
                max = 90
            ),
            ui.input_text(
                id = 'b_tz',
                label = 'Timezone',
                value = 'Pacific/Auckland'
            ),
            ui.input_action_button(
                id = 'search_place',
                label = 'Search places'
            )
        )
        return ui_out

    @render.ui
    def tajaka_year_choices():
        return ui.input_select(
            id = 'tajaka_year',
            label = '',
            choices = list(range(1900, 2200, 1)),
            selected = (
                datetime.now().year - 1
                if input.b_date().month > datetime.now().month
                else datetime.now().year -1 
                if (
                    input.b_date().day > datetime.now().day
                    and input.b_date().month == datetime.now().month
                )
                else datetime.now().year
            )
        )

    @render.ui
    def tajaka_divisional_choices():
        return ui.input_select(
            id = 'tajaka_divisional',
            label = '',
            choices = divisional_choices
        )

app = App(app_ui, server)
