## Running list of features to add, bloat to clean, etc.

### Feature list
- Ability to read from .jhd files (Jagannatha Hora savefiles)
- Tajaka annual charts
    - ~~Use tropical ayanamsa to find out birth Sun longitude~~
    - ~~In tropical ayanamsa, find time in that year when Sun reached same longitude~~
    - ~~Cast chart at that time in sideral ayanamsa~~
    - Explore otions to speed up tropical longitude search. e.g. `scipy.fsolve`?
    - ~~Add annual dasas~~
- Chart class
    - Clean functions
    - Add visuals
        - South Indian
        - Western
        - North Indian
        - East Indian
- Read stdout
    - ~~Is there need to write file out and read back in? Unnecessary disk IO?~~
- Vimsottari dasa
    - Recursive function produces dasa shares faster than loop. ~~Verify timings~~
    - ~~Add ability to shift dasa dates~~
- UI
    - ~~Move inputs to sidebar~~
    - ~~Group tabs as natal vs tajaka. So natal dasa and natal chart should be in one tab. Similarly for the tajaka chart (and the future tajaka dasa)~~
    - ~~viewport dimensions so that outputs can react to dimensions where default scaling isn't good enough~~
    - Clean dasa UI
- Yogas
    - Use BV Raman's 300 yogas as a reference
- Divisional charts
    - ~~D-1 varga table~~
    - D-2 varga table
    - D-3 varga table
    - D-4 varga table
    - D-7 varga table
    - D-9 varga table
    - D-10 varga table
    - D-12 varga table
    - D-16 varga table
    - D-20 varga table
    - D-24 varga table
    - D-27 varga table
    - D-30 varga table
    - D-40 varga table
    - D-45 varga table
    - D-60 varga table

### Bugs
- In the place selector, if "West Bengal" is selected, we get
> Object of type int64 is not JSON serializable
- In the place selector, if "Mumbai Suburban" is selected, it is overwritten by "Mumbai Suburban District" and the `update_birth_data_selected` bit of code runs twice.
