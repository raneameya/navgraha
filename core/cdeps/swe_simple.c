#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "swephexp.h"

double ipl_core(
    int year, int month, int day, int hour, int min, double sec,
    int ipl, int sid_bool, int sid_mode, double lon, double lat, 
    int speed_bool, const char *ephe_path
) {
    long iflag = SEFLG_SWIEPH;
    iflag |= SEFLG_SPEED;
    double tjd_tt, tjd_ut, tjd_et;
    double planet_lon;
    double planet_speed;
    char err[256];

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
    tjd_tt = dret[0];
    tjd_ut = dret[1];

    // Convert universal time to ephemeris time.
    tjd_et = tjd_ut + swe_deltat_ex(tjd_ut, iflag, err);

    if (ipl == -2) { // Ascendent
        int hsys = 'W';
        double cusps[13]; // Array for house cusps (1-12)
        double ascmc[10]; // Array for additional points (Asc, MC, etc.)
        double cusp_speed[37];
        double ascmc_speed[10];
        if (swe_houses_ex2(
                tjd_ut, iflag, lat, lon, hsys, cusps, 
                ascmc, cusp_speed, ascmc_speed, err
            ) == ERR) 
        {
            printf("Error calculating houses.\n");
            return -1.0;
        }
        planet_lon = ascmc[0];
        planet_speed = ascmc_speed[0];
    }
    // Calculate position using swe_calc (requires ET)
    else {
        double res[6];
        if (swe_calc(tjd_et, ipl, iflag, res, err) == ERR) {
            fprintf(stderr, "Error: %s\n", err);
            return -1.0;
        }
        planet_lon = res[0];
        planet_speed = res[3];
    }

    swe_close();
    if (speed_bool) {
        return planet_speed;
    } else {
        return planet_lon;
    }
}

double planet_info(
    int year, int month, int day, int hour, int min, double sec,
    int ipl, int sid_mode, double lon, double lat, int speed_bool, 
    const char *ephe_path
) {
    int is_ketu = 0;
    int is_bhrgu = 0;
    int sid_bool;
    double pl_lon, pl_speed, pl_lon_or_speed;

    if (ipl == -7) { // define true Ketu
        ipl = 11; // true Rahu
        is_ketu = 1;
    } else if (ipl == -3) { // define mean Ketu
        ipl = 10; // mean Rahu
        is_ketu = 1;
    } else if (ipl == -8) {// define Bhr̥gu Bindu
        is_bhrgu = 1;
    }

    if (sid_mode == -1) {
        sid_bool = 0;
    } else {
        sid_bool = 1;
    }

    if (is_ketu && speed_bool) {
        pl_speed = ipl_core(
            year, month, day, hour, min, sec, ipl, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        return pl_speed;
    } else if (is_ketu) {
        pl_lon = ipl_core(
            year, month, day, hour, min, sec, ipl, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        pl_lon = (pl_lon - 180.0) > 0 ? (pl_lon - 180.0) : (pl_lon + 180.0);
        return pl_lon;
    } else if (is_bhrgu && speed_bool) {
        double moon_speed, rahu_speed;
        // Use true rahu for now
        rahu_speed = ipl_core(
            year, month, day, hour, min, sec, 11, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        moon_speed = ipl_core(
            year, month, day, hour, min, sec, 1, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        return ((rahu_speed + moon_speed) / 2.0);
    } else if (is_bhrgu) {
        double moon_lon, rahu_lon, bb_lon;
        // Use true rahu for now
        rahu_lon = ipl_core(
            year, month, day, hour, min, sec, 11, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        moon_lon = ipl_core(
            year, month, day, hour, min, sec, 1, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        bb_lon = ((rahu_lon + moon_lon) / 2.0);
        if (moon_lon >= rahu_lon) {
            return bb_lon;
        } else {
            bb_lon += 180.0;            
        }
        return (bb_lon >= 360.0) ? bb_lon - 360.0 : bb_lon;
    } else {
        pl_lon_or_speed = ipl_core(
            year, month, day, hour, min, sec, ipl, sid_bool, 
            sid_mode, lon, lat, speed_bool, ephe_path
        );
        return pl_lon_or_speed;
    }
}

double sun_lon(
    int year, int month, int day, int hour, int min, double sec,
    int sid_mode, const char *ephe_path
) {
    int sid_bool;
    if (sid_mode == -1) {
        sid_bool = 0;
    } else {
        sid_bool = 1;
    }
    double sun_longitude = ipl_core(
        year, month, day, hour, min, sec, 0, sid_bool, 
        sid_mode, 0, 0, 0, ephe_path
    );
    return sun_longitude;
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
