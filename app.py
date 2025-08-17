from shiny import App, ui, render, req, reactive
from datetime import datetime, timedelta
from constants import rnp, ayanamsas, yr_len
import stdout_to_pd as std2pd
import misc_functions as mf
import chart as crt
import vimsottari_dasa as vd
import sol_cross as sc

table_nav_panel = ui.nav_panel(
    'Table',
    ui.include_js(path = 'js/viewport.js'),
    ui.output_text(id = 'birth_info_chart'),
    ui.output_data_frame(id = 'get_chart_data')
)

dasa_nav_panel = ui.nav_panel(
    'Daśa',
    ui.input_numeric(
        id = 'dasa_offset_days', 
        label = 'Offset daśa dates', 
        value = 0, step = 1
    ), 
    ui.input_select(
        id = 'vimsottari_dasa_sub_level',
        label = '',
        choices = {
            '0': 'Mahadaśā', '1': 'Antardaśā', '2': 'Pratyantardaśā',
            '3': 'Sookśmaantardaśā'#,'4':'Praanaantardaśā'
        }
    ),
    ui.output_text(id = 'birth_info_dasa'),
    ui.output_text(id = 'offset_info_dasa'),
    ui.output_data_frame(id = 'get_vimsottari_dasa')
)

tajaka_nav_panel = ui.nav_panel(
    'Tājaka',
    ui.output_ui(id = 'tajaka_year_choices'),
    ui.output_text(id = 'tajaka_info'),
    ui.output_data_frame(id = 'tajaka_chart_df')
)

moon_nav_panel = ui.nav_panel(
    'Lunar phase',
    #ui.output_data_frame(id='moon_phases')
    #output_widget(id='moon_phases')
)

app_ui = ui.page_fillable(
    ui.output_ui(id = 'birth_input'),
    ui.navset_card_tab(
        ui.nav_control(ui.input_switch(
            id = 'input_done', label = 'Show inputs', value = False
        )),
        ui.nav_spacer(),
        table_nav_panel,
        dasa_nav_panel,
        tajaka_nav_panel,
        #moon_nav_panel,
        ui.nav_control(ui.input_dark_mode()),
        id = 'pill'
    )
)

def server(input, output, session):

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
        # Close the place search modal on row being chosen
        ui.modal_remove()
        # Update the show input switch to close the input panel
        ui.update_switch(id = 'input_done', value = False)

    @reactive.calc
    def birth_chart():
        '''
        Return a chart object that can be reused across the app
        '''
        c = crt.chart(
            b_yr = input.b_date().year,
            b_mo = input.b_date().month,
            b_da = input.b_date().day,
            b_hr = int(input.b_time()[0:2]),
            b_mi = int(input.b_time()[3:5]),
            b_sc = int(input.b_time()[6:8]),
            b_lon = input.b_lon(),
            b_lat = input.b_lat(),
            b_tz = input.b_tz(),
            ay = input.b_ayanamsa(),
            place = input.b_place()
        )
        return c

    @render.data_frame
    def get_chart_data():
        p = birth_chart().placements
        # Round some cols
        p = mf.round_cols(p, ['Lon°', 'Speed'], [1, 3])
        # Keep subset
        p = p[[
            'Graha', 'Bhava', 'Rashi', 'Lon°', 'Nakshatra', 
            'Nakshatra lord', 'Pada', 'Speed'
        ]]
        return p

    @reactive.calc
    def natal_vimsottari_dasa():
        return vd.vimsottari_dasa(
            chart = birth_chart(), 
            sub_dasa_level = int(input.vimsottari_dasa_sub_level()), 
            dasa_offset_days = input.dasa_offset_days(),
            trunc_intervals = True
        )

    @render.data_frame
    def get_vimsottari_dasa():
        dasas = natal_vimsottari_dasa()
        # Currently, about 280px are used by other pills, radio buttons, 
        # headers, etc. This value may need to be changed in the future if 
        # more ui elements are added above this table.
        return render.DataGrid(
            data = dasas.dasa_to_df(), height = f'{input.height() - 280}px', 
            filters = int(input.vimsottari_dasa_sub_level()) > 0
        )

    @render.text
    def birth_info_chart():
        # To give user feedback about birth place & time selection
        return birth_chart().repr_str

    @render.text
    def offset_info_dasa():
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

    @render.text
    def birth_info_dasa():
        return birth_chart().repr_str

    @reactive.calc
    def tajaka_chart():
        args = mf.chart_kwargs(
            chart = birth_chart(), 
            dt = sc.sol_cross(
                yr = int(input.tajaka_year()), 
                birth_crt = birth_chart(), 
                tropical = True
            )
        )
        return crt.chart(**args)

    @render.data_frame
    def tajaka_chart_df():
        out = mf.round_cols(
            tajaka_chart().placements, ['Lon°', 'Speed'], [1, 3]
        )[[
            'Graha', 'Bhava', 'Rashi', 'Lon°', 'Nakshatra', 
            'Nakshatra lord', 'Pada', 'Speed'
        ]]
        return out

    @render.text
    def tajaka_info():
        return tajaka_chart().repr_str

    ## Lunar phases tab
    # @render_widget
    # def moon_phases():
    #     p=mf.lunar_phases(
    #         sweedir='./swisseph-master/', dt=birth_datetime(), tz=input.b_tz()
    #     )
    #     fig=px.line(data_frame=p, x='Datetime', y='Phase')
    #     fig.update_xaxes(dtick='w1', tickformat='%d %m')
    #     return fig

    @render.ui
    def birth_input():
        ui_out = ui.panel_conditional(
            'input.input_done',
            ui.row(
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
        )
        return ui_out

    @render.ui
    def tajaka_year_choices():
        return ui.input_select(
            id = 'tajaka_year',
            label = 'Tājaka year',
            choices = list(range(1900, 3000, 1)), 
            selected = datetime.now().year
        )

app = App(app_ui, server)
