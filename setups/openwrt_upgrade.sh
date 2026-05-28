# To recopy app from GitHub
tkn=xxx

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/.venv/lib/python3.13/site-packages/webbrowser.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/webbrowser.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/app/time_input.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/app/time_input.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/app/icons.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/app/icons.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/app/custom_nav_panel.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/app/custom_nav_panel.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/app/helper.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/app/helper.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/cdeps/swe_simple.c https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/cdeps/swe_simple.c

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart_minimal.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart_minimal.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart_plot_constants.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart_plot_constants.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/chart/chart_helpers.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/chart/chart_helpers.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/dasas/vimsottari_dasa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/dasas/vimsottari_dasa.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/data/lut.pickle https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/data/lut.pickle
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/data/constants.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/data/constants.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/data/nakshatra_pada_melt.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/data/nakshatra_pada_melt.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Rasi.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Rasi.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Navamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Navamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Hora.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Hora.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Drekkana.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Drekkana.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Chathurtamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Chathurtamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Saptamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Saptamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Dasamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Dasamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Dvadasamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Dvadasamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Sodasamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Sodasamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Vimsamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Vimsamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Siddhamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Siddhamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Nakshatramsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Nakshatramsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Trimsamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Trimsamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Khavedamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Khavedamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Aksavedamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Aksavedamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/Shashtiamsa.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/Shashtiamsa.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/divisionals/divisional_helpers.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/divisionals/divisional_helpers.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/js/custom.js https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/js/custom.js

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/misc_functions.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/misc_functions.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/stdout_to_pd.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/stdout_to_pd.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/fractional_interval.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/fractional_interval.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/misc/birth_event.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/misc/birth_event.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/panchanga/panchanga.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/panchanga/panchanga.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/sweadaptor/swisseph_reader.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/sweadaptor/swisseph_reader.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/sweadaptor/swisseph_adaptor.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/sweadaptor/swisseph_adaptor.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/sweadaptor/swe_helper.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/sweadaptor/swe_helper.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/tajaka/sol_cross.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/tajaka/sol_cross.py
wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/core/tajaka/get_sun_lon.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/core/tajaka/get_sun_lon.py

wget --header 'Authorization: token '"$tkn"'' -O /etc/chart_now/app.py https://raw.githubusercontent.com/raneameya/chart_now/refs/heads/main/app.py

cp core/cdeps/swe_simple.c swisseph-master/
cd /etc/chart_now/swisseph-master/
# The below should compile provided the makefile has been successfully compiled
gcc -fPIC -shared -o swe_simple.so swe_simple.c -L. -lswe
