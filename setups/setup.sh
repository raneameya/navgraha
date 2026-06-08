#!/bin/bash

## Clone repo
echo "Downloading repo"
gh repo clone raneameya/chart_now
cd chart_now

## Create py virtual env and install dependencies
echo "Setting up python environment and dependencies"
python -m venv ./.venv
source ./.venv/bin/activate
pip install --upgrade pip
pip install -e .

## Download and compile swiss ephemeris
echo "Downloading and setting up Swiss Ephemeris"
wget -O ./sweph.zip https://github.com/aloistr/swisseph/archive/refs/heads/master.zip
bsdtar -x -f ./sweph.zip -C .
rm ./sweph.zip
cd swisseph-master
make
cd ..
cp core/cdeps/swe_simple.c swisseph-master
cd swisseph-master
# The below should compile provided the makefile has been successfully compiled
gcc -fPIC -shared -o swe_simple.so swe_simple.c -L. -lswe
cd ..

## [Optional] Download and process the latest places.txt file
echo "Downloading latest place list"
wget -O ./places.zip https://download.geonames.org/export/dump/allCountries.zip
bsdtar -x -f ./places.zip -C .
rm ./places.zip
awk -v FS='\t' -v OFS='\t' '{ if ($15 != "" && $15 >= 1 && $18 != "") print $1, $2, $3, $5, $6, $9, $16, $15, $18 }' ./allCountries.txt > ./places.txt
rm ./allCountries.txt

## Run the app and make available on local network
shiny run --host 0.0.0.0 --port 8888
