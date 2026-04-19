from datetime import datetime, time
from zoneinfo import ZoneInfo

from shiny import App, ui, render, req, reactive

from core.data.constants import (
    rnp, ayanamsas, yr_len, divisional_choices
)
import core.misc.stdout_to_pd as std2pd
import core.misc.misc_functions as mf
import core.chart.chart as crt
from core.panchanga.panchanga import Panchanga
import core.dasas.vimsottari_dasa as vd
import core.tajaka.sol_cross as sc
from core.appui.icons import icon_gear
from core.appui.custom_nav_panel import (
    custom_nav_panel, dasa_sub_levels
)
from core.appui.time_input import input_time
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor

now = datetime.now()

divisional_choices_flat = {
    k: v for inner in divisional_choices.values() for k, v in inner.items()
}

natal_ui = custom_nav_panel(id = 'natal')

tājaka_ui = custom_nav_panel(id = 'tājaka')

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
        tājaka_ui,
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
        cmd = 'rg -i "' + input.b_place() + '" places.txt'
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
        # Updating inputs for user feedback should be in isolate scope
        # to avoid 
        with reactive.isolate():
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
        # Don't take a reactive dependency on place input
        with reactive.isolate():
            place = input.b_place()
            # Avoid downstream computation if place is empty
            req(place)
        be = BirthEvent(
            dt = datetime.combine(
                date = b_date, 
                time = time(b_hr, b_mi, b_sc), 
                tzinfo = ZoneInfo(input.b_tz())
            ), 
            latitude = input.b_lat(), 
            longitude = input.b_lon(), 
            z_height = 0, 
            place = place
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
        return getattr(
            natal_chart().divisionals, input.natal_divisional()
        )

    @render.plot
    def natal_plot():
        return natal_divisional().chart_plot(
            dark = input.dark_mode() == 'dark',
            style = input.chart_style(),
            title = divisional_choices_flat[input.natal_divisional()]
        )

    @render.data_frame
    def natal_table():
        return natal_divisional().display_table
    
    @render.data_frame
    def natal_panchanga():
        return Panchanga(birth_chart = natal_chart()).df()

    @reactive.calc
    def natal_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = natal_chart(),
            divisional = input.natal_divisional(),
            sub_dasa_level = int(input.natal_vimsottari_dasa_sub_level()),
            dasa_offset_days = input.natal_dasa_offset_days(),
            trunc_intervals = True
        )

    @render.data_frame
    def natal_vimsottari_dasa_df():
        dasas = natal_vimsottari_dasa()
        # Adjust number below to increase/decrease table height
        return render.DataGrid(
            data = dasas.dasa_to_df(), height = f'{input.height() - 250}px',
            filters = int(input.natal_vimsottari_dasa_sub_level()) > 0
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
    def tājaka_chart():
        args = mf.chart_kwargs(
            chart = natal_chart(),
            dt = sc.sol_cross(
                yr = int(input.tājaka_year()),
                birth_crt = natal_chart(),
                tropical = True
            )
        )
        return crt.chart(**args)
    
    @reactive.calc
    def tājaka_divisional():
        return getattr(tājaka_chart().divisionals, input.tājaka_divisional())

    @render.plot
    def tājaka_plot():
        return tājaka_divisional().chart_plot(
            dark = (input.dark_mode() == 'dark'),
            style = input.chart_style(),
            title = divisional_choices_flat[input.tājaka_divisional()]
        )

    @render.data_frame
    def tājaka_table():
        out = tājaka_divisional().display_table
        return out
 
    @render.data_frame
    def tājaka_panchanga():
        p = Panchanga(birth_chart = tājaka_chart())
        return p.df()

    @render.text
    def tājaka_info():
        return tājaka_chart().repr_str

    @reactive.calc
    def tājaka_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = tājaka_chart(),
            divisional = input.tājaka_divisional(),
            sub_dasa_level = int(input.tājaka_vimsottari_dasa_sub_level()),
            dasa_offset_days = input.tājaka_dasa_offset_days(),
            trunc_intervals = True,
            lifespan = 1
        )

    @render.text
    def tājaka_dasa_offset_info():
        dasa_offset_days = tājaka_vimsottari_dasa().dasa_offset_days
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
    def tājaka_vimsottari_dasa_df():
        dasas = tājaka_vimsottari_dasa()
        return render.DataGrid(
            data = dasas.dasa_to_df(),
            # Adjust number below to increase/decrease table height
            height = f'{input.height() - 300}px',
            filters = int(input.tājaka_vimsottari_dasa_sub_level()) > 0
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
    def tājaka_year_choices():
        return ui.input_select(
            id = 'tājaka_year',
            label = '',
            choices = list(range(1900, 2200, 1)),
            selected = (
                now.year - 1 if input.b_date().month > now.month
                else now.year - 1 
                if (
                    input.b_date().day > now.day
                    and input.b_date().month == now.month
                )
                else now.year
            )
        )

app = App(app_ui, server)
