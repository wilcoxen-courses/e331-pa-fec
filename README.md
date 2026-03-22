# Exercise: Mapping 2020 Political Contributions in Pennsylvania

## Summary

This exercise maps contributions to presidential candidates by party in the 2020 election for zip codes in Pennsylvania.

## Input Data

Several input files are available from the class Google Drive folder: **contrib_clean.pkl**, a pickled version of the aggregated individual contribution data from the previous exercise on campaign contributions; **com_cand_info.csv**, another file from the previous assignment that links committees, candidates, and parties; and **cb_2020_42_zcta520_500k.gpkg**, a geopackage file containing two layers: `state`, which is the boundary for Pennsylvania itself, and `zip`, which has boundaries for all of the state's ZCTAs (zip code tabulation areas, or just zip codes below). See the tips section if you're interested in what the `_500k` in the file name means.

## Deliverables

There are seven deliverables: a script called **pop.py** that retrieves population data from the Census API server; one called **by_party.py** that aggregates the contribution data to parties rather than candidates (different from what was done in the previous exercise); a script called **join.py** that joins the population and contribution results onto the zip layer in the geopackage file to build a new geopackage file called `"joined.gpkg"`; a QGIS project file called **contrib.qgz**, and three images: **map_party.png**, **map_pc.png** and **map_funds.png**.

## Instructions

### A. Script pop.py

1. _Get the populations of Pennsylvania zip codes._ Follow the approach used in a couple of the previous exercises to retrieve Census variable `B01001_001E`, the total population, using a `for` clause of `"zip code tabulation area:*"` and no `in` clause. Please use the **2020** ACS5 to match the year of the election. The `in` clause is omitted because the API doesn't allow it with zip codes after 2019, so the query will return data for the whole country. Finally, omit `"NAME"` from the query: it just restates the zip code and is not helpful here.

1. Build a dataframe called `pop` from the server's response.

1. Use a dictionary called `new_names` to rename columns `"B01001_001E"` to `"pop"` (same as the dataframe itself) and `"zip code tabulation area"` to `"zip"`.

1. Set the index of `pop` to `"zip"` and then use `.sort_index()` to sort the dataframe by zip code.

1. Save the dataframe to `"pop.csv"`.

### B. Script by_party.py

1. Import modules as needed.

1. Read the contributions data in `"contrib_clean.pkl"` into a variable called `contrib`.

1. Read the committee data in `"com_cand_info.csv"` into a dataframe called `com_cand`.

1. _Join the committee information onto the contributions._ Create a variable called `merged` by using an inner join to merge `com_cand` onto `contrib` using `"CMTE_ID"` as the join key and specifying `validate="m:1"`. Since it's an inner join, omit the indicator variable since all the output records will always be `"both"`. The inner join eliminates a few 2019 contributions to a committee that didn't actually field a candidate in 2020.

1. Use a dictionary to rename `"CAND_PTY_AFFILIATION"` to `"party"`.

1. _Select the Pennsylvania data from the full dataset._ Create a variable called `pa` by using `.query()` to select the rows of `merged` where `"STATE"` is equal to `"PA"`.

1. _Group the Pennsylvania data by zip code and political party._ Create a variable called `grouped` by using `.groupby()` to group `pa` by `"zip"` and `"party"`.

1. _Find total contributions by zip code and party._ Create variable `amount` by applying `.sum()` to column `"amt"` of `grouped`.

1. Some of the amounts are negative because campaigns sometimes repay contributors. We'll use the `.where()` method to set those to zero. Set `amount` to the result of calling the `.where()` method on `amount` with the arguments `amount>0` and `0`. (FAQ 1)

1. _Summarize contributions by zip code._ Set `wide` to the result of calling `.unstack()` on `amount` using the argument `"party"`. The result will be a dataframe with one row per zip code and one column per party.

1. A lot of the values in `wide` will be missing because there aren't contributions to every party in every zip code. Set those to zero by setting `wide` equal to the result of calling `.fillna(0)` on `wide`.

1. _Find total contributions in each zip code._ Add a column to `wide` called `"total"` that is equal to applying `.sum()` to `wide` with `axis="columns"`.

1. Save `wide` to `"by_party.csv"`. Have a look at it to make sure it is roughly what you'd expect. (However, if you're familiar with Pennsylvania you may notice that some of the zip codes are clearly wrong. Actual Pennsylvania zip codes are in the range 15xxx to 19xxx but some of the original contributions that list Pennsylvania as the state have zip codes outside that range. Those will be removed in a later step.)

### C. Script join.py

1. Import the numerical python module `numpy` as `np` and import other modules as needed

1. _Read the population data._ Create variable `pop` by reading `pop.csv`. Use a dictionary to set `dtype` for `"zip"` to `str`. The `dtype` setting is less crucial here than in other contexts because none of the legitimate zip codes start with leading zero. However, if you work with US data you'll make your life easier if you get in the habit of **always** reading FIPS and zip codes as strings.

1. _Read the GIS layer of zip code boundaries._ Now read the zip code layer of geopackage file by setting `geo_zip` to the result of calling `gpd.read_file()` with arguments `"cb_2020_42_zcta520_500k.gpkg"` and `layer="zip"`.

1. Rename `geo_zip` column `"ZCTA5CE20"` to `"zip"`.

1. Eliminate several extraneous columns by trimming `geo_zip` down to its `"zip"` and `"geometry"` columns. An easy way to do this is by setting `geo_zip` to its subset for the list of columns `["zip","geometry"]` via `geo_zip[["zip","geometry"]]`

1. _Join the population data onto zip code boundaries_. Set `geo_pa` to the value of merging `pop` onto `geo_zip`. Use `"zip"` as the join key and set `how` to `"left"`, which will filter out the populations for all zip codes that aren't in Pennsylvania. Also, set validate to `"1:1"` and set `indicator` to `True`.

1. Print the value counts of the merge indicator and then drop it. The count for `"left_only"` shows the number of Pennsylvania zip codes that had no population.

1. _Read the contribution data._ Create variable `contrib` by reading `"by_party.csv"`. Set the `dtype` for `"zip"` to `str`.

1. _Join the contribution data onto the spatial data._ Create variable `both` by merging `contrib` onto `geo_pa` using an outer one-to-one join with `"zip"` as the join key and `indicator` set to `True`.

1. _Check the merge._ Print the value counts for the merge indicator. Not everything will be `"both"`: expect to see more than 400 for `"left_only"` (zip codes that had no contributions from addresses in Pennsylvania) and more than 100 for `"right_only"` (invalid zip codes and those for post office boxes, which aren't included in the zip code shape file).

1. _Check the contributions by merge result._ Create `grouped` by grouping `both` by `"_merge"`. Include the argument `observed=True` in the `.groupby()` call to avoid a warning about a future change in Pandas. Then create `summary` by applying the `.agg()` method to column `"total"` of `grouped` using the argument `["count","sum","mean"]`. The result will be a dataframe with three columns of aggregate information: the record count for each case of `"_merge"`, and the sum and the mean as well.

1. Print `summary`. You should see that about $168k, a small part of the total, came from unmatchable `"right_only"` zip codes. Note that these are totals by zip code, so the means are much larger than a typical individual contribution.

1. _Select the usable data._ Now set `trim` to the result of using `.query()` to pick out the records of `both` where `"_merge"` is equal to `"both"`, and then add `.copy()` to the end of the statement to cause Pandas to create a copy of the data rather than a view.

1. Drop `"_merge"` from `trim`.

1. Compute per capita contributions by zip code by setting column `"pc"` of `trim` to the `"total"` column divided by the `"pop"` column.

1. _Ignore per capita results for small counties._ The per capita values are very large in a few zip codes with small populations and large contributions. To focus on larger counties, set the per capita column to numpy's missing data value, `np.nan`, for counties with less than `100` people by setting `trim["pc"]` equal to the result of applying `.where()` to `trim["pc"]` using arguments `trim["pop"]>=100` and `np.nan`.

1. Next create a column called `"d_share"` in `trim` giving the share of total contributions that went to Democratic candidates.

1. _Save the joined layer._ Write out the joined layer to layer `"zip"` of geopackage `"joined.gpkg"` by calling `.to_file()` on `trim` using arguments `"joined.gpkg"` and `layer="zip"`. Note that if `"joined.gpkg"` already exists, this call will add (or replace) layer `"zip"` but won't affect any other layers. To be sure that you get a clean copy of the file, you may want to remove any existing version of `"joined.gpkg"` before running this part of the script.

1. _Save the state border._ For convenience, now read the state boundary layer from the original geopackage file by setting `geo_state` to the result of using `gpd.read_file()` to read `"cb_2020_42_zcta520_500k.gpkg"` with `layer="state"`. Then use the `.to_file()` method to write it out to `"joined.gpkg"` using `layer="state"`.

1. Now drop column `"geometry"` from `trim`.

1. Sort `trim` by `"zip"` using `.sort_values()`.

1. Save `trim` as `"join.csv"` using `index=False`. Note that the name is `"join.csv"` to match the name of the script for clarity when looking at the directory in the future.

### D. Maps map_party.png, map_pc.png and map_funds.png

1. Start QGIS and load both layers from `"joined.gpkg"`.

1. _Build a map showing the party balance in contributions._ Start by dragging the state layer to the bottom of the list. Then set its fill color to black and its fill style to "FDiagonal". That will be useful because some of the zip codes have missing data, which has the effect of creating holes in layers that use graduated styling. The shading will make it easy to tell where that has happened because it will only be visible where the overlying data is missing. If you look carefully, you'll see that happen right away because there are two small parts of the state that have no zip code. See the Tips section for a brief explanation about places with no zip code.

1. Right-click on the zip layer and rename it to `party` for clarity. Then set its style to "Graduated" using `"d_share"` as the value, set the color ramp to `RdBu`, and set the mode to **Pretty Breaks** using 5 classes. This is where the striped state layer really pays off: it makes it easy to tell the difference between missing data (striped) and places where the `d_share` variable leads to the area being white (not striped).

1. The map will a little look better if you make lines showing the zip codes thinner. To do that, click on the colored area in the "Symbol" section of the "Graduated" settings (click on the color, not the drop down arrow). Then click on the "Simple Fill" symbol, scroll down until "Stroke width" is visible, and then click the down arrow next to it a couple of times until "Hairline" appears. Then click "Apply".

1. Export the map as `"map_party.png"`.

1. _Build a map showing per capita contributions._ The party map shows the mix of contributions but it's only part of the story because it doesn't say anything about the intensity of contributions from each zip code. To get at that, we'll look at per capita contributions. Duplicate the `party` layer and rename it `pc`. Then turn off the `party` layer by unchecking its box and turn on the new `pc` layer. Change the variable driving the "Graduated" style to `"pc"`, change the color ramp to "Greens", set the mode to **Natural Breaks**, and use 4 classes. If all goes well, you should see that per capita contributions are actually very small for most of the state. However, they are very high for some zip codes near Philadelphia (on the east), and fairly high for some near Pittsburgh (on the west) and at a few other places scattered around the state.

1. Export the map as an image to `"map_pc.png"`.

1. _Build a map showing overall funding by party and zip code._ The maps above show the preferences of people in different zip codes but they don't convey overall fundraising. To get at that, we'll build a map with pie charts indicating total funding by party from each zip code. Duplicate the `pc` layer and rename it `funds`. Then turn off `pc` and turn on `funds`. Set the style for `funds` to "Single Symbol" and set the fill color to something pretty light. Then add pie diagrams. For the pie attributes, choose `"DEM"` and `"REP"` and set the colors to blue and red. Then set the size of the pies to "Scaled Size" using the `"total"` attribute for scaling. Click "Find" to find the maximum value of `"total"`, and then set the "Size" to 15. Make sure that the "Size Units" selector at the top of the dialog is set to millimeters.

1. Export the map to `"map_funds.png`".

1. Save the QGIS project file as `"contrib.qgz`".

## Submitting

Once you're happy with everything and have committed all of the changes to your local repository, please push the changes to GitHub. At that point, you're done: you have submitted your answer.

## Tips

+ The cartographic boundary files are lower resolution, and hence smaller in file size, than TIGER/Line files. They are very suitable for thematic maps (such as the one in this exercise) where precise distance measurements are not needed. The files are available at several scales: the 500k here indicates that the file is at a scale of 1:500,000, which is the highest resolution among the cartographic boundary options. The US zip code map is about 60 MB at this resolution; for comparison, the TIGER/Line version is about nine times larger: about 530 MB.

+ Some areas of the United States do not have ZCTAs. They are usually rural areas with very low population density. There are a couple of spots in Pennsylvania without ZCTAs. For comparison, there are considerably more areas without them in New York, largely in the Adirondack region, and vastly more in the western US.

+ This exercise is just scratching the surface of what could be done to analyze the contributions data. Many other variables could be added as well, including median income, race, education, employment status, and so on.

## FAQs

1. _How does the `.where()` method work?_

    It's a little counterintuitive, at least at first. When called like this, `B = A.where(test,C)`, it says that each element of `B` should be equal to the corresponding element of `A` when the corresponding element of `test` is True; otherwise, the value of `B` should be set to `C` instead of what was in `A`.
