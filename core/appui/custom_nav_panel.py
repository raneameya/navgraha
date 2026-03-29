from shiny import ui

dasa_sub_levels = {
    '0': 'Mahadaśā', '1': 'Antardaśā', '2': 'Pratyantardaśā',
    '3': 'Sookśmaantardaśā'#, '4': 'Praanaantardaśā', '5': 'Dehaantardaśā'
}
divisional_choices = {
    'rasi': 'Rāśi', 'navamsa': 'Navāmśā', 'hora': 'Horā', 
    'shashtiamsa_trd': 'Ṣaṣṭyāṃśa (trd)', 'shashtiamsa_rev': 'Ṣaṣṭyāṃśa (rev)'
}

def custom_nav_panel(id: str):

    chart_ui = ui.accordion_panel(
        'Chart',
        ui.output_plot(id = f'{id}_plot')
    )
    table_ui = ui.accordion_panel(
        'Table',
        ui.output_data_frame(id = f'{id}_table')
    )
    panchanga_ui = ui.accordion_panel(
        'Pañcāṅga',
        ui.output_data_frame(id = f'{id}_panchanga')
    )
    dasa_ui = ui.accordion_panel(
        'Daśa',
        ui.row(
            ui.input_numeric(
                id = f'{id}_dasa_offset_days',
                label = '# days to offset daśa (+ve/-ve)',
                value = 0, step = 1
            ),
            ui.input_select(
                id = f'{id}_vimsottari_dasa_sub_level',
                label = 'Daśā level',
                choices = dasa_sub_levels
            )
        ),
        ui.output_text(id = f'{id}_dasa_offset_info'),
        ui.output_data_frame(id = f'{id}_vimsottari_dasa_df')
    )
    select_divisional_ui = ui.input_select(
        id = f'{id}_divisional',
        label = '',
        choices = divisional_choices
    )
    custom_select_ui = ui.layout_column_wrap(
        select_divisional_ui,
        ui.output_ui(id = f'{id}_year_choices')
    ) if id == 'tājaka' else select_divisional_ui
    nav_panel = ui.nav_panel(
        id.capitalize(),
        ui.output_text(id = f'{id}_info'),
        custom_select_ui,
        ui.accordion(
            chart_ui,
            table_ui,
            panchanga_ui,
            dasa_ui
        )
    )

    return nav_panel
