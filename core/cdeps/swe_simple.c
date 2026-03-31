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

void ipl_core_arr(
    double tjd_ut, double tjd_et, long iflag, int ipl, double lon, 
    double lat, double result[2]
) {
    char err[256];
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
        }
        result[0] = ascmc[0];
        result[1] = ascmc_speed[0];
    }
    // Calculate position using swe_calc (requires ET)
    else {
        double res[6];
        if (swe_calc(tjd_et, ipl, iflag, res, err) == ERR) {
            fprintf(stderr, "Error: %s\n", err);
        }
        result[0] = res[0];
        result[1] = res[3];
    }
}

void planet_info_arr(
    int ipl_arr[], int n_planets, int year, int month, int day, int hour, 
    int min, double sec, int sid_mode, double lon, double lat, 
    const char *ephe_path, double lon_arr[], double speed_arr[]
) {
    int is_ketu = 0, is_bhrgu = 0, width = 13;
    int ipl;
    char pname[40];
    long iflag = SEFLG_SWIEPH;
    iflag |= SEFLG_SPEED;
    double tjd_tt, tjd_ut, tjd_et;
    char err[256];

    // Set SWE path
    if (ephe_path[0]) {
        swe_set_ephe_path(ephe_path);
    } else {
        printf("Warning: Enter path to epehemeris files using -edir<path>.");
        printf("Defaulting to Moshier formulae\n");
        swe_set_ephe_path(NULL);
    }

    if (sid_mode != -1) {
        // Set sidereal mode, sid_mode = -1 is tropical
        swe_set_sid_mode(sid_mode, 0, 0);
        iflag |= SEFLG_SIDEREAL;
    }

    // Convert UTC date/time to Julian Day (UT1)
    double dret[2];
    swe_utc_to_jd(year, month, day, hour, min, sec, SE_GREG_CAL, dret, err);
    tjd_tt = dret[0];
    tjd_ut = dret[1];

    // Convert universal time to ephemeris time. tjd_et and tjd_tt are slightly off!
    tjd_et = tjd_ut + swe_deltat_ex(tjd_ut, iflag, err);

    for (int i = 0; i < n_planets; i++) {
        ipl = ipl_arr[i];
        double lon_speed[2];
        is_ketu = 0;
        is_bhrgu = 0;

        if (ipl == -7) { // define true Ketu
            ipl = 11; // true Rahu
            is_ketu = 1;
        } else if (ipl == -3) { // define mean Ketu
            ipl = 10; // mean Rahu
            is_ketu = 1;
        } else if (ipl == -8) {// define Bhr̥gu Bindu
            is_bhrgu = 1;
        }

        if (is_ketu) {
            ipl_core_arr(
                tjd_ut, tjd_et, iflag, 11, lon, lat, lon_speed
            );
            if (lon_speed[0] >= 180.0) {
               lon_speed[0] -= 180.0;
            } else {
                lon_speed[0] += 180.0;
            }
        } else if (is_bhrgu) {
            double rahu_lon_speed[2];
            // Use mean Rahu for Bhr̥gu Bindu calcs
            ipl_core_arr(
                tjd_ut, tjd_et, iflag, 1, lon, lat, lon_speed
            );
            ipl_core_arr(
                tjd_ut, tjd_et, iflag, 10, lon, lat, rahu_lon_speed
            );
            double moon_lon = lon_speed[0], rahu_lon = rahu_lon_speed[0];
            for (int j = 0; j < 2; j++) {
                lon_speed[j] = (lon_speed[j] + rahu_lon_speed[j]) / 2.0;
            }
            if (moon_lon < rahu_lon) {
                lon_speed[0] += 180.0;
                lon_speed[0] = (lon_speed[0] >= 360.0) 
                                ? lon_speed[0] - 360.0 
                                : lon_speed[0];
            }
        } else {
            ipl_core_arr(
                tjd_ut, tjd_et, iflag, ipl, lon, lat, lon_speed
            );
        }
        lon_arr[i] = lon_speed[0];
        speed_arr[i] = lon_speed[1];
    }
    swe_close();
}
