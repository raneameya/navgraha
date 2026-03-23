## New setup instructions in openwrt router

## Install required system packages
opkg update
opkg install python3 python3-pip python3-venv gcc bsdtar nano-full git git-http make

## Fetch latest chart_now repo
cd /etc/
git clone https://raneameya:ghp_tkn@github.com/raneameya/chart_now.git

## Initialise a python venv
cd /etc/chart_now
python -m venv ./.venv
source ./.venv/bin/activate
pip install --upgrade pip
pip install -e .
mv webbrowser.py .venv/lib/python3.13/site-packages/

## Download and compile swisseph components
wget -O ./sweph.zip https://github.com/aloistr/swisseph/archive/refs/heads/master.zip
bsdtar -x -f ./sweph.zip -C .
rm ./sweph.zip
cd ./swisseph-master
nano Makefile #edit out (delete) the "-ldl" flag in linux
./swetest -edir./ephe -topo77.19763,28.5673,0 -b10.8.1983 -utc03:10 -rise -n2 -hindu
# Create shared library from swe_simple for python get_sun_lon
cp /etc/chart_now/core/cdeps/swe_simple.c .
# The below should compile provided the makefile has been successfully compiled
gcc -fPIC -shared -o swe_simple.so swe_simple.c -L. -lswe
cd ..

## [Optional]Download and process places.txt file
wget -O ./places.zip https://download.geonames.org/export/dump/allCountries.zip
bsdtar -x -f ./places.zip -C .
rm ./places.zip
awk -v FS='\t' -v OFS='\t' '{ if ($15 != "" && $15 >= 1 && $18 != "") print $1, $2, $3, $5, $6, $9, $16, $15, $18 }' ./allCountries.txt > ./places.txt
rm ./allCountries.txt

## Run the app
shiny run --host 0.0.0.0 --port 1506
# Place below in local startup tab
cd /etc/chart_now/ && source /etc/chart_now/.venv/bin/activate && shiny run --reload --host 0.0.0.0 --port 1506 /etc/chart_now/app.py &&
