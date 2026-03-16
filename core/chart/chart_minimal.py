import core.misc.misc_functions as mf
import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib import collections as mc
from core.chart.chart_plot_constants import *
import warnings

class chart_minimal:
    '''
    A minimal chart class, that strips away any requirement that a chart 
    is a valid celestial configuration for a given time. 
    Mostly useful for plotting divisional charts 
    (e.g. Rahu & Ketu can be in the same house)
    '''
    def __init__(
        self,
        placements:pd.DataFrame, 
        display_cols: list[str]
    ):
        # Assumed that placements contains the necessary info 
        # about grahas, degrees, speed, etc.
        self.placements = placements
        cols = placements.columns.tolist()
        # display_cols should be a subset of cols. if not, choose only 
        # intersection. display_cols can potentially be exposed to the 
        # user in the form of a multiselect dropdown
        set_display_cols = set(display_cols)
        set_cols = set(cols)
        if set_display_cols > set_cols:
            diff_cols = set_display_cols.difference(set_cols)
            warnings.warn(f'''
            {diff_cols} not present in this chart. 
            Table will exclude these column(s).
            ''')
            display_cols = list(set_cols.intersection(set_display_cols))
        display_table = placements[display_cols]
        # Columnwise precision
        precision = {'Speed': 3, 'Lon°': 0}
        # Truncate cols
        for x in ['Speed', 'Lon°']:
            if x in display_cols:                
                display_table = mf.round_cols(
                    display_table, [x], [precision[x]]
                )
        self.display_table = display_table
    
    def __repr__(self):
        return self.placements.__repr__()

    def chart_plot(
            self, 
            dark:bool, 
            style:str,
            title:str = 'D-1', 
            rasis:dict = rasi_dict # mapping sign to unicode glyph
        ):
            # Colour to draw lines, grahas, signs 
            # Almost anything drawn is in this colour.
            writecolour = 'white' if dark else 'black'
            # Background colour, matches theme bootstrap background colour
            bgcolour = '#1D1F21' if dark else 'white'
            # South Indian charts are anchored by sign, 
            # and North Indian are anchored charts by house
            house_or_sign = {
                'South Indian': 'Sign', 'North Indian': 'Bhava'
            }[style]
            # Get the placements of grahas. Sorting allows for the planets 
            # to be shown in the order of progession in a sign
            p = self.placements[[
                'Graha', 'Bhava', 'Rāśi', 'Sign', 'Speed', 'Lon'
            ]].sort_values(by = 'Lon')
            # Convert to dictionary for easy subsetting. Setting graha as index 
            # allows graha to be the keys of the resulting dict
            p.set_index('Graha', inplace = True)
            grahas = p.to_dict(orient = 'index')
            # Need to find offset for signs for North Indian chart
            rasi_symbol_start = {
                'South Indian': 1, 'North Indian': grahas['Lagna']['Sign']
            }[style]
            # Cyclically shift rasis so that Lagna is in first house
            rasis = mf.cyclic_shift(x = rasis, start = rasi_symbol_start - 1)
            rasis = {str(i + 1): rasis[k] for i, k in enumerate(rasis)}
            # Begin plotting
            fig, ax = plt.subplots(dpi = 120)
            # Plot polygons for each house. 
            # Useful in future if need to highlight some houses
            # Currently does effectively nothing with colours set as 'None'
            for h_num, h_shp in house_shapes[style].items():
                ax.add_patch(plt.Polygon(
                    h_shp, edgecolor = 'None', facecolor = 'None'
                ))
            # Plot wireframe of chart
            ax.add_collection(mc.LineCollection(
                chart_frame[style], colors = writecolour, linewidths = 0.5
            ))
            # Lagna needs to be plotted for NI charts as degrees are mentioned
            # if style == 'North Indian':
            #     del grahas['Lagna']
            # Plot grahas in bhavas, loop over 12 bhavas
            for i in list(range(1, 13, 1)):
                str_i = str(i)
                # Add Unicode symbol of rasi to bhava
                ax.annotate(
                    text = rasis[str_i][1],
                    # Offset rasi symbol by for each house
                    xy = coord_plus(
                        t1 = house_start_coords[style][str_i],
                        t2 = rasi_icon_offset[style][str_i]
                    ), 
                    horizontalalignment = 'center', 
                    verticalalignment = 'center',
                    alpha = 0.5, fontsize = 8, color = writecolour
                )
                # List of grahas in bhava_i
                grahas_i = [g for g in grahas if grahas[g][house_or_sign] == i]
                # Add grahas to bhava_i
                if grahas_i is not []:
                    num_grahas_in_house = len(grahas_i)
                    for g_num, g in enumerate(grahas_i):
                        # Style text for graha
                        g_txt = g[0:2]
                        # Degrees graha has progressed in sign
                        deg_txt = f'''{round(grahas[g]['Lon'] % 30, 1):.1f}'''
                        if grahas[g]['Speed'] >= 0:
                            # Doubly subscripted text indicating degrees
                            txt = (r'$\mathrm{' + g_txt 
                            + r'_{_{' + deg_txt + r'}}}$')
                        else:
                            # Overbar for retro graha
                            txt = (r'$\overline{\mathrm{' 
                            + g_txt + r'}}_{_{' + deg_txt + r'}}$')
                        ax.annotate(
                            text = txt, 
                            xy = coord_plus(
                                t1 = house_start_coords[style][str_i],
                                t2 = graha_coords_offset[style][str_i][
                                    str(num_grahas_in_house)
                                ][g_num]
                            ), color = writecolour,
                            horizontalalignment = 'center', 
                            verticalalignment = 'center'
                        )
            ax.set_xlim(0, 4)
            ax.set_ylim(0, 4)
            fig.set_facecolor(bgcolour)
            plt.axis('off')
            plt.title(title, color = writecolour)
            fig.tight_layout()
            return fig
