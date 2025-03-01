library(data.table)
wd <- '/media/ameya/Data/Programming/chart_now/'
rnp <- fread(text = 'Nakshatra	Pada-1	Pada-2	Pada-3	Pada-4
Ashwini	Aries	Taurus	Gemini	Cancer
Bharani	Leo	Virgo	Libra	Scorpio
Krittika	Sagittarius	Capricorn	Aquarius	Pisces
Rohini	Aries	Taurus	Gemini	Cancer
Mrigsira	Leo	Virgo	Libra	Scorpio
Ardra	Sagittarius	Capricorn	Aquarius	Pisces
Punarvasu	Aries	Taurus	Gemini	Cancer
Pushya	Leo	Virgo	Libra	Scorpio
Ashlesha	Sagittarius	Capricorn	Aquarius	Pisces
Magha	Aries	Taurus	Gemini	Cancer
Purva Phalguni	Leo	Virgo	Libra	Scorpio
Uttar Phalguni	Sagittarius	Capricorn	Aquarius	Pisces
Hasta	Aries	Taurus	Gemini	Cancer
Chitra	Leo	Virgo	Libra	Scorpio
Swati	Sagittarius	Capricorn	Aquarius	Pisces
Vishakha	Aries	Taurus	Gemini	Cancer
Anuradha	Leo	Virgo	Libra	Scorpio
Jyeshtha	Sagittarius	Capricorn	Aquarius	Pisces
Moola	Aries	Taurus	Gemini	Cancer
Purva Ashada	Leo	Virgo	Libra	Scorpio
Uttar Ashada	Sagittarius	Capricorn	Aquarius	Pisces
Shravan	Aries	Taurus	Gemini	Cancer
Dhanistha	Leo	Virgo	Libra	Scorpio
Satabhisha	Sagittarius	Capricorn	Aquarius	Pisces
Purva Bhadrapada	Aries	Taurus	Gemini	Cancer
Uttar Bhadrapada	Leo	Virgo	Libra	Scorpio
Revati	Sagittarius	Capricorn	Aquarius	Pisces')
rnp[, Nakshatra := factor(Nakshatra, levels = Nakshatra)]
rnp <- melt.data.table(
  data = rnp, id.vars = 'Nakshatra', variable.name = 'Pada', 
  value.name = 'Rashi', variable.factor = FALSE, value.factor = TRUE
)
setorderv(rnp, 'Nakshatra')
rnp[, c('Rashi', 'Nakshatra lord', 'Vimshottari dasa (yrs)') := {
  rashi <- factor(rep(Rashi[1:12], each = 9), levels = Rashi[1:12])
  v_lord <- rep(rep(c(
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 
    'Saturn', 'Mercury'
  ), each = 4), times = 3)
  v_length <- rep(rep(c(
    7, 20, 6, 10, 7, 18, 16, 19, 17
  ), each = 4), times = 3)/4
  list(rashi, v_lord, v_length)
}]
setcolorder(rnp, c(
  'Rashi', 'Nakshatra', 'Nakshatra lord', 'Vimshottari dasa (yrs)'
))
rnp[, Pada := gsub(pattern = 'ada-', replacement = '', x = Pada)]
setorderv(rnp)
rnp[, c('Start', 'End') := list(
  seq(from = 0, by = MASS::fractions(10/3), length.out = 108), 
  seq(from = MASS::fractions(10/3), by = MASS::fractions(10/3), length.out = 108)
)]
fwrite(rnp, paste0(wd, 'rnp.csv'))
