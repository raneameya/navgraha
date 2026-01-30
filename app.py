from shiny import App, ui, render, req, reactive
from datetime import datetime, timedelta
from constants import rnp, ayanamsas, yr_len
import stdout_to_pd as std2pd
import misc_functions as mf
import chart as crt
import vimsottari_dasa as vd
import sol_cross as sc
import matplotlib.pyplot as plt

dasa_sub_levels = {
    '0': 'Mahadaśā', '1': 'Antardaśā', '2': 'Pratyantardaśā',
    '3': 'Sookśmaantardaśā'#, '4': 'Praanaantardaśā', '5': 'Dehaantardaśā'
}

natal_chart_ui = ui.accordion_panel(
    'Chart',
    ui.output_plot(id = 'natal_plot')
)

natal_table_ui = ui.accordion_panel(
    'Positions',
    ui.output_data_frame(id = 'get_chart_data')
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
    ui.accordion(
        natal_chart_ui,
        natal_table_ui,
        natal_dasa_ui
    )
)

tajaka_chart_ui = ui.accordion_panel(
    'Chart',
    ui.output_plot(id = 'tajaka_plot')
)

tajaka_table_ui = ui.accordion_panel(
    'Positions',
    ui.output_data_frame(id = 'tajaka_chart_df')
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
    ui.output_ui(id = 'tajaka_year_choices'),
    ui.output_text(id = 'tajaka_info'),
    ui.accordion(
        tajaka_chart_ui,
        tajaka_table_ui,
        tajaka_dasa_ui
    )
)

app_ui = ui.page_sidebar(
    # Sidebar needs to be open so that the birth inputs (e.g. date, time, 
    # ayanamsa) are initialised.
    ui.sidebar(
        ui.output_ui(id = 'birth_input'),
        title = 'Birth inputs', open = 'open', id = 'sidebar'
    ),
    ui.include_js(path = 'js/viewport.js'),
    ui.navset_card_tab(
        natal_ui,
        tajaka_ui,
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
    def natal_chart():
        '''
        Return a chart object that can be reused across the app
        '''
        inputs = {
            'b_yr': input.b_date().year,
            'b_mo': input.b_date().month,
            'b_da': input.b_date().day,
            'b_hr': int(input.b_time()[0:2]),
            'b_mi': int(input.b_time()[3:5]),
            'b_sc': int(input.b_time()[6:8]),
            'b_lon': input.b_lon(),
            'b_lat': input.b_lat(),
            'b_tz': input.b_tz(),
            'ay': input.b_ayanamsa(),
            'place': input.b_place()
        }
        c = crt.chart(**inputs)
        return c
    
    @render.plot
    def natal_plot():
        return natal_chart().chart_plot(
            dark = input.dark_mode() == 'dark',
            style = input.chart_style()
        )

    @render.data_frame
    def get_chart_data():
        p = natal_chart().rasi
        # Round some cols
        p = mf.round_cols(p, ['Lon°', 'Speed'], [1, 3])
        # Keep subset
        p = p[[
            'Graha', 'Lon°', 'Nakshatra',
            'Nakshatra lord', 'Pada', 'Speed'
        ]]
        return p

    @reactive.calc
    def natal_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = natal_chart(),
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
        return natal_chart().repr_str

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

    @render.plot
    def tajaka_plot():
        return tajaka_chart().chart_plot(
            dark = (input.dark_mode() == 'dark'),
            style = input.chart_style()
        )

    @render.data_frame
    def tajaka_chart_df():
        out = mf.round_cols(
            tajaka_chart().rasi, ['Lon°', 'Speed'], [1, 3]
        )[[
            'Graha', 'Lon°', 'Nakshatra',
            'Nakshatra lord', 'Pada', 'Speed'
        ]]
        return out

    @render.text
    def tajaka_info():
        return tajaka_chart().repr_str

    @reactive.calc
    def tajaka_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = tajaka_chart(),
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
                label = 'Input date',
                value = datetime.today().strftime('%Y-%m-%d'),
                format = 'yyyy-mm-dd',
                weekstart = 0,
                autoclose = True
            ),
            ui.input_text(
                id = 'b_time',
                label = 'Input time',
                value = datetime.now().strftime('%H:%M:%S')
            ),
            ui.input_select(
                id = 'b_ayanamsa',
                label = 'Choose Ayanamsa',
                choices = ayanamsas.to_dict(),
            ),
            ui.input_select(
                id = 'chart_style',
                label = 'Chart style',
                choices = ['South Indian', 'North Indian']
            ),
            ui.input_text(
                id = 'b_place',
                label = 'Enter place',
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
            selected = datetime.now().year
        )

app = App(app_ui, server)
