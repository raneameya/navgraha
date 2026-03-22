## Clone repo
gh repo clone raneameya/chart_now
cd chart_now

## Create py virtual env and install dependencies
python -m venv ./.venv
source ./.venv/bin/activate.fish
pip install --upgrade pip
pip install -e .

## Download and compile swiss ephemeris
wget -O ./sweph.zip https://github.com/aloistr/swisseph/archive/refs/heads/master.zip
bsdtar -x -f ./sweph.zip -C .
rm ./sweph.zip
cd swisseph-master
make
cd ..

## [Optional] Download and process the latest places.txt file
wget -O ./places.zip https://download.geonames.org/export/dump/allCountries.zip
bsdtar -x -f ./places.zip -C .
rm ./places.zip
awk -v FS='\t' -v OFS='\t' '{ if ($15 != "" && $15 >= 1 && $18 != "") print $1, $2, $3, $5, $6, $9, $16, $15, $18 }' ./allCountries.txt > ./places.txt
rm ./allCountries.txt
