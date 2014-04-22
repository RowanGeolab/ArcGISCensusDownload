import arcpy
import urllib2, json, os, sys, traceback

censusAPIkey = "insert_your_key_here"
# enter your Census API key above
# request an API key here:
# http://www.census.gov/developers/tos/key_request.html


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Census Download Tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CDExtent]


class CDExtent(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Census Download - By Extent"
        self.description = "Download GIS data from the Census using a defined extent."
        self.canRunInBackground = False
        self.supportedGeometries = ['Tract', 'Block Group', 'Block']
        self.censustables = {
                "H0030001": {"alias": "Housing units", "type": "LONG"},
                "H0030003": {"alias": "Vacant housing units", "type": "LONG"},
                "H0040001": {"alias": "Occupied housing units", "type": "LONG"},
                "H0040002": {"alias": "Owned with a mortgage or a loan", "type": "LONG"},
                "H0040003": {"alias": "Owned free and clear", "type": "LONG"},
                "H0040004": {"alias": "Renter occupied", "type": "LONG"},
                "P0010001": {"alias": "Population", "type": "LONG"}
            }

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Download Area Extent",
            name="in_extent",
            datatype="GPExtent",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Census Geometry Types",
            name="in_geometry",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param1.filter.type = "ValueList"
        param1.filter.list = self.supportedGeometries

        param2 = arcpy.Parameter(
            displayName="Census Tables",
            name="in_tables",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param2.filter.type = "ValueList"
        param2.filter.list = map(lambda x: "{0} - {1}".format(x, self.censustables[x]['alias']), sorted(self.censustables.keys())) 
        
        param3 = arcpy.Parameter(
            displayName="Output Feature Class",
            name="out_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        param3.filter.list = ['Local Database', 'Remote Database']
            
        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        try:
            mxd = arcpy.mapping.MapDocument("CURRENT") # current map document
            df = arcpy.mapping.ListDataFrames(mxd)[0]  # first data frame
            sr = df.spatialReference                   # spatial reference of the data frame

            et = (parameters[0].valueAsText).split(" ")
            in_extent = arcpy.Extent(*et)
            in_extent.spatialReference = sr
            if not (in_extent.spatialReference.PCSCode == 4326):
                in_extent = in_extent.projectAs(arcpy.SpatialReference(4326))
            
            for geom in (parameters[1].valueAsText).split(";"):
                self.processCensus(in_extent, geom, parameters[2].valueAsText, parameters[3].valueAsText, messages)
        except Exception as e:
            messages.addMessage(e)
            messages.addMessage(traceback.format_exc())
        return

    def processCensus(self, in_extent, geom, tables, out_fc, messages):
        # create a new Census Geometry layer
        geom = geom.replace("'", "")
        out_fc = str(out_fc+"_"+geom).replace(" ", "_")
        if(arcpy.Exists(out_fc)):
            arcpy.Delete_management(out_fc)
        censuspath = arcpy.CreateFeatureclass_management(os.path.dirname(out_fc), os.path.basename(out_fc), "POLYGON", "", "DISABLED", "DISABLED", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "", "0", "0", "0")
        censuspath = censuspath.getOutput(0)
        arcpy.AddField_management(censuspath, "state", "TEXT", "", "", "2", "State", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(censuspath, "county", "TEXT", "", "", "3", "County", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(censuspath, "tract", "TEXT", "", "", "6", "Tract", "NULLABLE", "NON_REQUIRED", "")

        ## fields to be exposed in the Census cursor
        curfld = ["SHAPE@", "state", "county", "tract"]

        if(geom in self.supportedGeometries):
            if(geom == "Tract"):
                geourl = "http://tigerweb.geo.census.gov/arcgis/rest/services/Tracts_Blocks/MapServer/10/query?where=&text=&objectIds=&geometryType=esriGeometryEnvelope&geometry={0},{1},{2},{3}&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=STATE,COUNTY,TRACT&returnGeometry=true&outSR=4326&returnIdsOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson".format(in_extent.XMin, in_extent.YMin, in_extent.XMax, in_extent.YMax)
                apiurl = "http://api.census.gov/data/2010/sf1?key={k}&get={tbl}&for=tract:{t}&in=state:{s}+county:{c}"
            if(geom == "Block Group"):
                geourl = "http://tigerweb.geo.census.gov/arcgis/rest/services/Tracts_Blocks/MapServer/11/query?where=&text=&objectIds=&geometryType=esriGeometryEnvelope&geometry={0},{1},{2},{3}&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=STATE,COUNTY,TRACT,BLKGRP&returnGeometry=true&outSR=4326&returnIdsOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson".format(in_extent.XMin, in_extent.YMin, in_extent.XMax, in_extent.YMax)
                apiurl = "http://api.census.gov/data/2010/sf1?key={k}&get={tbl}&for=block+group:{bg}&in=state:{s}+county:{c}+tract:{t}"
                arcpy.AddField_management(censuspath, "blockgroup",  "TEXT", "", "", "2", "Block Group", "NULLABLE", "NON_REQUIRED", "")
                curfld.append("blockgroup")
            if(geom == "Block"):
                geourl = "http://tigerweb.geo.census.gov/arcgis/rest/services/Tracts_Blocks/MapServer/12/query?where=&text=&objectIds=&geometryType=esriGeometryEnvelope&geometry={0},{1},{2},{3}&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=STATE,COUNTY,TRACT,BLOCK&returnGeometry=true&outSR=4326&returnIdsOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson".format(in_extent.XMin, in_extent.YMin, in_extent.XMax, in_extent.YMax)
                apiurl = "http://api.census.gov/data/2010/sf1?key={k}&get={tbl}&for=block:{b}&in=state:{s}+county:{c}+tract:{t}"                            
                arcpy.AddField_management(censuspath, "block",  "TEXT", "", "", "4", "Block", "NULLABLE", "NON_REQUIRED", "")
                curfld.append("block")
        else:
            return False

        # retrieve the Census Geometry from the TigerWeb ArcGIS Server
        response = urllib2.urlopen(geourl)
        geod = json.loads(response.read())

        # if no features returned, provide a warning and stop
        if(len(geod['features']) == 0):
            messages.addErrorMessage("No Census Geometries located. Is your extent within the United States?")
            raise arcpy.ExecuteError
        
        for field in tables.replace("'","").split(";"):
            f = field.split(" - ")[0]
            if(f in self.censustables.keys()):
                arcpy.AddField_management(censuspath, f, self.censustables[f]['type'], "", "", "", self.censustables[f]['alias'], "NULLABLE", "NON_REQUIRED", "")
                curfld.append(f)

        global censusAPIkey
        if censusAPIkey == "insert_your_key_here":
            messages.addErrorMessage("Invalid Census API key. Please modify this ")
            raise arcpy.ExecuteError

        cursor = arcpy.da.InsertCursor(censuspath, curfld)
        for feat in geod['features']:
            polygon = arcpy.Polygon(arcpy.Array(map(lambda x: arcpy.Point(x[0], x[1]), feat['geometry']['rings'][0])), arcpy.SpatialReference(4326))
            geoattr = feat['attributes']
            if geom == "Block":
                curval = [polygon, geoattr["STATE"], geoattr["COUNTY"], geoattr["TRACT"], geoattr["BLOCK"]]
                tblurl = apiurl.format(k=censusAPIkey,b=geoattr["BLOCK"],t=geoattr["TRACT"],c=geoattr["COUNTY"],s=geoattr["STATE"],tbl=",".join(curfld[5:]))
            elif geom == "Block Group":
                curval = [polygon, geoattr["STATE"], geoattr["COUNTY"], geoattr["TRACT"], geoattr["BLKGRP"]]
                tblurl = apiurl.format(k=censusAPIkey,bg=geoattr["BLKGRP"],t=geoattr["TRACT"],c=geoattr["COUNTY"],s=geoattr["STATE"],tbl=",".join(curfld[5:]))
            else:
                curval = [polygon, geoattr["STATE"], geoattr["COUNTY"], geoattr["TRACT"]]
                tblurl = apiurl.format(k=censusAPIkey,t=geoattr["TRACT"],c=geoattr["COUNTY"],s=geoattr["STATE"],tbl=",".join(curfld[4:]))
            
            # request the data from the Census API
            response = urllib2.urlopen(tblurl)
            apid = json.loads(response.read())
            
            if(geom == "Tract"):
                curval.extend(apid[1][:-3])
            else:
                curval.extend(apid[1][:-4])            
            cursor.insertRow( curval )
        del cursor
        return True