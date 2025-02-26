from shiny import App, ui, render, req, reactive
from datetime import datetime
import stdout_to_pd as std2pd
import misc_functions, pytz, numpy

table_nav_panel=ui.nav_panel(
    'Table',
    ui.output_text(id='b_time_place'),
    ui.output_data_frame(id='get_chart_data')
)

app_ui = ui.page_fillable(
    ui.output_ui(id='user_input'),
    ui.navset_card_tab(
        ui.nav_control(ui.input_switch(
            id='input_done', label='Show inputs', value=True
        )),
        ui.nav_spacer(),
        table_nav_panel,        
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

    # Update values in input fields based on row selection by user
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
        bdt=misc_functions.create_date_from_txt(
            yr=input.b_date().year,
            mo=input.b_date().month,
            da=input.b_date().day,
            hr=int(input.b_time()[0:2]),
            mi=int(input.b_time()[3:5]),
            se=int(input.b_time()[6:8]),
            tz=input.b_tz()
        )
        return bdt

    # Once a single row of birth place is chosen, calculate the date and time 
    # in UTC
    @reactive.calc
    def birth_datetime_args():        
        bdt=birth_datetime()
        # Convert to UTC
        birth_datetime_utc=bdt.astimezone(pytz.utc)
        # Create birthdate input for swetest
        birth_date='-b'+birth_datetime_utc.strftime('%d.%m.%Y')
        # Create birthtime input for swetest
        birth_time='-utc'+birth_datetime_utc.strftime('%H:%M.%S')
        return [birth_date, birth_time]

    @render.data_frame
    def get_chart_data():
        # Get birthdate arguments for swetest
        birth_datetime_utc_args=birth_datetime_args()
        # location argument
        location='-geopos'+str(input.b_lon())+','+str(input.b_lat())+',0'
        wd = '/media/ameya/Data/Programming/Astro/swisseph-master/'
        # User inputs
        input_args = birth_datetime_utc_args+[location]
        p=misc_functions.swetest(sweedir=wd, birth_args=input_args)
        lagna=p[p['Graha']=='Lagna'].iloc[0].at['Lon']
        p=p[['Graha', 'House', 'Lon°', 'Speed','Lat°']] 
        # Need to truncate house decimals
        p['House']=(numpy.ceil(p['House']-1)%12)+1
        # Keep classical planets (including Rahu, Ketu)
        p=p.head(12)
        # Add lagna details
        signs=[
            'Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi'
        ]
        lagna_sign=signs[int(lagna//30)]        
        p.iloc[0,0]='Lagna ('+lagna_sign+')'        
        return p
    
    @render.text
    def b_time_place():
        # To give user feedback about birth place & time selection
        bdt=birth_datetime().strftime('%d-%m-%Y %H:%M:%S %Z')
        location=input.b_place()
        return location + ', ' + bdt
    
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
