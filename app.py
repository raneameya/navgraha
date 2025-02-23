from shiny import App, ui, render, req, reactive
from datetime import datetime
import stdout_to_pd as std2pd
import pytz
import pandas as pd

ui_sidebar=ui.sidebar(
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
        placeholder='Auckland'
    ),
    ui.input_numeric(
        id='b_lon',
        label='Longitude',
        value=0,
        min=-180,
        max=180
    ),
    ui.input_numeric(
        id='b_lat',
        label='Latitude',
        value=0,
        min=-90,
        max=90
    ),
    ui.input_text(
        id='b_tz',
        label='Timezone',
        placeholder='Pacific/Auckland'
    )
)

input_nav_panel=ui.nav_panel(
    'Input',
    #ui.output_text('birth_data_input'), # convenient print statement
    ui.output_data_frame('birth_lat_lon')
)

table_nav_panel=ui.nav_panel(
    'Table',
    ui.output_data_frame('get_chart_data')
)

app_ui = ui.page_sidebar(
    ui_sidebar,
    ui.navset_card_tab(
        input_nav_panel,
        table_nav_panel,
        ui.nav_control(ui.input_dark_mode()),
        id='pill'
    )
)

def server(input, output, session):

    rvals=reactive.Value({'b_input_entered':False})

    @render.text
    def birth_data_input():        
        birth_input = [
            input.b_date().strftime('%d.%m.%Y'), str(input.b_time()), input.b_place(), 
            str(input.b_lon()), str(input.b_lat()), input.pill()
        ]        
        return ' '.join(birth_input)

    @render.data_frame
    def birth_lat_lon():
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

    # Update values in input fields based on row selection by user
    @reactive.effect
    def update_birth_data_selected():
        place_selected=birth_lat_lon.data_view(selected=True)   
        if len(input.b_place()) < 3:
            # If too few characters entered, ignore birth place input
            birth_lat_lon.update_data(None)
            rvals.set({'b_input_entered':False})
        elif len(input.b_place()) >= 3:
            # When enough characters entered and row chosen, update inputs
            # for lon, lat, place & tz based on selection 
            req(not place_selected.empty)
            lon=place_selected.longitude.iloc[0]
            lat=place_selected.latitude.iloc[0]
            place=place_selected.name.iloc[0]
            tz=place_selected.timezone.iloc[0]
            ui.update_numeric('b_lon', value=lon)
            ui.update_numeric('b_lat', value=lat)
            ui.update_text('b_place', value=place)
            ui.update_text('b_tz', value=tz)
            rvals_new=rvals.get()
            rvals_new['lat']=lat
            rvals_new['lon']=lon
            rvals_new['tz']=tz
            rvals.set(rvals_new)
    
    # Once a single row of birth place is chosen, calculate the date and time 
    # in UTC
    @reactive.calc
    def convert_birth_datetime_to_utc():
        req(input.b_tz())
        # Need to specify initial datetime without timezone
        birth_datetime=datetime(
            year=input.b_date().year,
            month=input.b_date().month,
            day=input.b_date().day,
            hour=int(input.b_time()[0:2]),
            minute=int(input.b_time()[3:5]),
            second=int(input.b_time()[6:7]),
            tzinfo=None
        )
        # Create local timezone object
        local_tz=pytz.timezone(input.b_tz())
        # Then localise the initial datetime object without timezone
        birth_datetime=local_tz.localize(birth_datetime)
        # Convert to UTC
        birth_datetime_utc=birth_datetime.astimezone(pytz.utc)
        # Create birthdate input for swetest
        birth_date='-b'+birth_datetime_utc.strftime('%d.%m.%Y')
        # Create birthtime input for swetest
        birth_time='-utc'+birth_datetime_utc.strftime('%H:%M.%S')
        return [birth_date, birth_time]

    @render.data_frame
    def get_chart_data():
        birth_datetime_utc=convert_birth_datetime_to_utc()
        location='-geopos'+str(input.b_lon())+','+str(input.b_lat())+',0'
        wd = '/media/ameya/Data/Programming/Astro/swisseph-master/'
        edir = wd + 'ephe'
        binary = [wd + 'swetest']
        common_args = ['-pp', '-head', '-edir' + edir]
        input_args = [birth_datetime_utc[0], birth_datetime_utc[1], location]
        config_args = ['-sid29', '-fTPlLsBgG']
        format_args = [
            '| sed -E \'s/(UT\\s\\S+)(\\s{1,2})(\\w)/\\1_\\3/g\'', 
            '| sed -E \'s/° /°/g\'', '| sed -E "s/\' /\'/g\"'
        ]
        colnames = [
            'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Speed', 
            'Lat', 'House', 'House°'
        ]
        p=std2pd.read_stdout(
            cmd=' '.join(
                binary + common_args + input_args + config_args + format_args
            ), reader='table', sep='\s+', col_names=colnames
        )
        return p

app = App(app_ui, server)
