# To recopy app
tkn=xxx
# Add the standard library webbrowser to the site-packages as it is not 
# included in the OpenWRT package system
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/lib/python3.11/site-packages/webbrowser.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/webbrowser.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/appui/time_input.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/appui/time_input.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/appui/icons.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/appui/icons.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/cdeps/swe_simple.c https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/cdeps/swe_simple.c

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart_minimal.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart_minimal.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart_plot_constants.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart_plot_constants.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart_helpers.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart_helpers.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/dasas/vimsottari_dasa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/dasas/vimsottari_dasa.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/data/lut.pickle https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/data/lut.pickle
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/data/constants.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/data/constants.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/data/nakshatra_pada_melt.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/data/nakshatra_pada_melt.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Navamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Navamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Rasi.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Rasi.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/divisional_helpers.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/divisional_helpers.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/js/custom.js https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/js/custom.js

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/misc_functions.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/misc_functions.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/stdout_to_pd.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/stdout_to_pd.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/fractional_interval.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/fractional_interval.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/birth_event.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/birth_event.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/panchanga/panchanga.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/panchanga/panchanga.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/sweadaptor/swisseph_reader.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/sweadaptor/swisseph_reader.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/sweadaptor/swisseph_adaptor.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/sweadaptor/swisseph_adaptor.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/tajaka/sol_cross.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/tajaka/sol_cross.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/tajaka/get_sun_lon.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/tajaka/get_sun_lon.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/app.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/app.py
