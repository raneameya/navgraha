#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "swephexp.h"

double planet_lon(
    int year, int month, int day, int hour, int min, double sec,
    int ipl, int sid_bool, int sid_mode, const char *ephe_path
) {
    long iflag = SEFLG_SWIEPH;
    double tjd, tjd_ut, tjd_et, res[6];
    char err[256];
    char pname[40];
    int is_ketu = 0;

    // ipl = -7, -3 as True Ketu, Mean Ketu respectively
    if (ipl == -7) {
        ipl = 11; // true Rahu
        is_ketu = 1;
    } else if (ipl == -3) {
        ipl = 10; // mean Rahu
        is_ketu = 1;
    }
    
    // To get planet name: swe_get_planet_name(ipl, pname);

    // Set SWE path
    if (ephe_path[0]) {
        swe_set_ephe_path(ephe_path);
    } else {
        printf("Warning: Enter path to epehemeris files using -edir<path>.");
        printf("Defaulting to Moshier formulae\n");
        swe_set_ephe_path(NULL);
    }
    
    // Set sidereal mode if required
    if (sid_bool) {
        swe_set_sid_mode(sid_mode, 0, 0);
        iflag |= SEFLG_SIDEREAL;
    }

    // Convert UTC date/time to Julian Day (UT1)
    double dret[2];
    swe_utc_to_jd(year, month, day, hour, min, sec, SE_GREG_CAL, dret, err);
    tjd_ut = dret[0];
    tjd = dret[1];

    // Convert universal time to ephemeris time
    tjd_et = tjd + swe_deltat_ex(tjd, iflag, err);
    // printf("tjd_et is %.15f.\n", tjd_et);

    // Calculate position using swe_calc (requires ET/TT)
    if (swe_calc(tjd_et, ipl, iflag, res, err) == ERR) {
        fprintf(stderr, "Error: %s\n", err);
        return 1;
    }

    swe_close();

    double planet_lon;
    planet_lon = res[0];
    if (is_ketu) {
        planet_lon += 180.0;
        if (planet_lon >= 360.0) {
            planet_lon -= 360.0;
        }
    }
    
    return planet_lon;
}

int main() {
    double lon = planet_lon(1991, 6, 15, 3, 10, 49, 0, 1, 29, "./ephe");
    printf("Longitude: %.7f\n", lon);
    return 0;
}

/*
Planet names for reference
#define SE_ECL_NUT              -1
#define SE_SUN                  0
#define SE_MOON                 1
#define SE_MERCURY              2
#define SE_VENUS                3
#define SE_MARS                 4
#define SE_JUPITER              5
#define SE_SATURN               6
#define SE_URANUS               7
#define SE_NEPTUNE              8
#define SE_PLUTO                9
#define SE_MEAN_NODE            10
#define SE_TRUE_NODE            11
#define SE_MEAN_APOG            12
#define SE_OSCU_APOG            13
#define SE_EARTH                14
#define SE_CHIRON               15
#define SE_PHOLUS               16
#define SE_CERES                17
#define SE_PALLAS               18
#define SE_JUNO                 19
#define SE_VESTA                20
#define SE_INTP_APOG            21
#define SE_INTP_PERG            22
#define SE_NPLANETS             23
#define SE_FICT_OFFSET           40    // offset for fictitious objects
#define SE_NFICT_ELEM           15
#define SE_PLMOON_OFFSET         9000  // offset for planetary moons
#define SE_AST_OFFSET           10000 // offset for asteroids
// Hamburger or Uranian "planets" 
#define SE_CUPIDO               40
#define SE_HADES                41
#define SE_ZEUS                 42
#define SE_KRONOS               43
#define SE_APOLLON              44
#define SE_ADMETOS              45
#define SE_VULKANUS             46
#define SE_POSEIDON             47
// other fictitious bodies
#define SE_ISIS                 48
#define SE_NIBIRU               49
#define SE_HARRINGTON           50
#define SE_NEPTUNE_LEVERRIER     51
#define SE_NEPTUNE_ADAMS         52
#define SE_PLUTO_LOWELL          53
#define SE_PLUTO_PICKERING       54
*/
