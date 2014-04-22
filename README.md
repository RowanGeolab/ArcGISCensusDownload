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

Output should be specified as a geodatabase feature class. Aliases for field names will be included in the output feature class. 

## License
&copy; 2014 John Reiser, Rowan University

[Licensed under the GPLv3.](https://www.gnu.org/copyleft/gpl.html)
