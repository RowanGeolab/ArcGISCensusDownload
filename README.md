# Census Download Toolbox for ArcGIS

A [Python Toolbox](http://resources.arcgis.com/en/help/main/10.2/index.html#//001500000022000000) for ArcGIS Desktop (specifically ArcMap) to make quick retrieval of Census information.

## Census API Key
In order for the toolbox to work properly, the CensusDownload.pyt Python Toolbox must be updated with a valid Census API key. 

A Census API key can be requested from the [Census API key request page](http://www.census.gov/developers/tos/key_request.html). 

## Download By Extent
Within the **Census Download - By Extent** tool, a user can specify an area of interest (such as the current map extent) and download Census tracts, block groups, and/or blocks, along with associated Census data. When run from ArcMap, the Census Download tool will reproject the specified extent as necessary, provided the primary data frame in ArcMap has a projection/coordinate system defined. 

Census Geometries for the 2010 Decennial Census:

- Tract
- Block Group
- Blocks

Census Tables from the 2010 Decennial Census:

- H0030001: Housing units
- H0030003: Vacant housing units
- H0040001: Occupied housing units
- H0040002: Owned with a mortgage or a loan
- H0040003: Owned free and clear
- H0040004: Renter occupied
- P0010001: Population
- P0100002: Population of one race
- P0100003: Population of one race: White alone
- P0100004: Population of one race: Black or African American alone
- P0100005: Population of one race: American Indian and Alaska Native alone
- P0100006: Population of one race: Asian alone
- P0100007: Population of one race: Native Hawaiian and Other Pacific Islander alone
- P0100008: Population of one race: Some Other Race alone
- P0100009: Population of one race: Two or More Races
- P0110002: Hispanic or Latino
- P0110003: Not Hispanic or Latino
- P0120002: Male
- P0120026: Female

Tables can be easily added to the script by altering the `censustables` dict in the tool source. Suggestions welcome regarding additional tables to be included in this default list. 

Output should be specified as a geodatabase feature class. Aliases for field names will be included in the output feature class. 

## Screenshot
![Screenshot of Census Download tool.](https://raw.githubusercontent.com/RowanGeolab/ArcGISCensusDownload/master/arcgispythontoolbox.png)

## License
&copy; 2014 John Reiser, Rowan University

[Licensed under the GPLv3.](https://www.gnu.org/copyleft/gpl.html)
