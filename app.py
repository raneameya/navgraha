from shiny import App, ui, render, req, reactive
from datetime import datetime
from constants import rnp
#from shinywidgets import output_widget, render_widget
import stdout_to_pd as std2pd, misc_functions as mf#, plotly.express as px

table_nav_panel=ui.nav_panel(
    'Table',
    ui.output_text(id='b_time_place'),
    ui.output_data_frame(id='get_chart_data')
)

moon_nav_panel=ui.nav_panel(
    'Lunar phase',
    #ui.output_data_frame(id='moon_phases')
    #output_widget(id='moon_phases')
)

app_ui = ui.page_fillable(
    ui.output_ui(id='user_input'),
    ui.navset_card_tab(
        ui.nav_control(ui.input_switch(
            id='input_done', label='Show inputs', value=False
        )),
        ui.nav_spacer(),
        table_nav_panel,
        #moon_nav_panel,
        ui.nav_control(ui.input_dark_mode()),
        id='pill'
    )
)

def server(input, output, session):

    rvals=reactive.Value({'b_input_entered':False})

    @render.data_frame
    def filtered_places():
        # Avoid updating table for small inputs (i.e. large searches in file)
        req(len(input.b_place()) >= 3)
        # Filter file for only matches to entered birth place
        cmd='grep -i "' + input.b_place() + '" places.txt'
        # Column names as reference. Not used as explained below
        colnames=[
            'geonameid', 'name', 'asciiname', 'latitude', 'longitude', 
            'country code', 'elevation', 'population', 'timezone'
        ]
        # Providing column names makes it ignore column names present in file
        places=std2pd.read_stdout(
            cmd=cmd, reader='csv', sep='\t', col_names=colnames            
        )
        places=places.sort_values(by=['population'], ascending=False)
        return render.DataGrid(places, selection_mode='rows')
    
    @reactive.effect
    @reactive.event(input.search_place)
    def input_modal():
        # Modal containing places
        m=ui.modal(
            ui.output_data_frame(id='filtered_places'),
            title='Click on a place to confirm details',
            easy_close=True,
            size='xl'
        )
        ui.modal_show(m)

    # Update values in input fields based on place selection by user
    @reactive.effect
    def update_birth_data_selected():
        place_selected=filtered_places.data_view(selected=True)   
        if len(input.b_place()) < 3:
            # If too few characters entered, ignore birth place input
            filtered_places.update_data(None)
            rvals.set({'b_input_entered':False})
        elif len(input.b_place()) >= 3:
            # When enough characters entered and row chosen, update inputs
            # for lon, lat & tz based on selection
            req(not place_selected.empty)
            lon=place_selected.longitude.iloc[0]
            lat=place_selected.latitude.iloc[0]
            place=place_selected.name.iloc[0]
            tz=place_selected.timezone.iloc[0]
            ui.update_numeric('b_lon', value=lon)
            ui.update_numeric('b_lat', value=lat)            
            ui.update_text('b_tz', value=tz)
            ui.update_text('b_place', value=place)
            # Update the show input switch to close the input panel
            ui.update_switch(id='input_done', value=False)
            # Close the place search modal on row being chosen
            ui.modal_remove()
    
    @reactive.calc
    def birth_datetime():
        bdt=mf.create_date_from_txt(
            yr=input.b_date().year,
            mo=input.b_date().month,
            da=input.b_date().day,
            hr=int(input.b_time()[0:2]),
            mi=int(input.b_time()[3:5]),
            se=int(input.b_time()[6:8]),
            tz=input.b_tz()
        )
        return bdt

    @render.data_frame
    def get_chart_data():
        # Get birthdate arguments for swetest
        birth_datetime_utc_args=mf.birth_datetime_args(birth_datetime())
        # location argument
        location='-geopos'+str(input.b_lon())+','+str(input.b_lat())+',0'
        wd = './swisseph-master/'
        # User inputs
        input_args = birth_datetime_utc_args+[location]
        p=mf.swetest(sweedir=wd, birth_args=input_args)
        # Keep classical planets (including Rahu, Ketu)
        p=p.head(10)
        # Add other details
        add_cols=['Rashi', 'Nakshatra', 'Nakshatra lord', 'Pada']
        p=mf.add_non_equi_col(
            p1=p, 
            p2=rnp,
            p1col='Lon',
            p2col_low='Start',
            p2col_high='End',
            p2col_get=add_cols
        )
        # Round some cols
        p=mf.round_cols(p, ['Lon°', 'Speed'], [1, 3])
        # Keep subset
        p=p[[
            'Graha', 'Bhava', 'Rashi', 'Lon°', 'Nakshatra', 
            'Nakshatra lord', 'Pada', 'Speed'
        ]]
        return p
    
    @render.text
    def b_time_place():
        # To give user feedback about birth place & time selection
        bdt=birth_datetime().strftime('%d-%m-%Y %H:%M:%S %Z')
        location=input.b_place()
        return location + ' ' + bdt
    
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
    def user_input():
        ui_out=ui.panel_conditional(
            'input.input_done',
            ui.row(
                ui.input_date(
                    id='b_date',
                    label='Input date',                
                    value=datetime.today().strftime('%Y-%m-%d'),        
                    format='yyyy-mm-dd',            
                    weekstart=0,            
                    autoclose=True            
                ), 
                ui.input_text(
                    id='b_time',
                    label='Input time',        
                    value=datetime.now().strftime('%H:%M:%S')
                ),
                ui.input_text(
                    id='b_place',
                    label='Enter place',
                    value='Auckland'
                ),
                ui.input_numeric(
                    id='b_lon',
                    label='Longitude',
                    value=174.74304,
                    min=-180,
                    max=180
                ),
                ui.input_numeric(
                    id='b_lat',
                    label='Latitude',
                    value=-36.85582,
                    min=-90,
                    max=90
                ),
                ui.input_text(
                    id='b_tz',
                    label='Timezone',
                    value='Pacific/Auckland'
                ),
                ui.input_action_button(
                    id='search_place',
                    label='Search places'
                )
            )            
        )
        return ui_out

app = App(app_ui, server)
