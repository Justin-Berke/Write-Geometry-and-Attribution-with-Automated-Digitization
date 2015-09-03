# This script was developed to automate the process of digitizing line features
#   that originate at each point in a large point grid, and extend radially
#   for 10000 meters, at 5° intervals

import arcpy
from arcpy import da # Data Access Module for interacting with features
from math import radians, sin, cos # Trig functions for calculating offsets

# Set data references using double backslashes
fetchGrid = "D:\\GIS Projects\\NWS - Fetch Vectors\\data\\Fetch_Vectors.mdb\\FetchVectorGrid_2500SqM"
fetchVectors = "D:\\GIS Projects\\NWS - Fetch Vectors\\data\\Fetch_Vectors.mdb\\test_data\\TestLineGeometry"
fields = ["FK_FetchVectorID", "Bearing", "SHAPE@"] # Fields to search
vectorDistance = 650000

# Count features in fetch grid & convert value to integer
result = arcpy.GetCount_management(fetchGrid)
count = int(result.getOutput(0))

# Loop through each grid point starting at FK_GridID = 1
for i in range(1, count + 1): # i is a counter
    # Write a query experssion to select one grid point at a time
    expression = arcpy.AddFieldDelimiters(fetchGrid, "FK_GridID") + " = %s" % (i)
    # Run the selection query
    with arcpy.da.SearchCursor(fetchGrid,("Easting", "Northing"), where_clause=expression) as cursor:
        # Step through the current selection and run the main process
        for row in cursor:
        	# Record the current coordinates that were attributed in the input point dataset
            eastingStart = row[0]
            northingStart = row[1]
            ##Test: print(str(northing) + ", " + str(easting))
            #
            # Draw 10km lines at 5° intervals (distance set in vectorDistance)
            for j in range(0, 72): # j is another counter
                eastingEnd = eastingStart + (vectorDistance * (sin(radians(j * 5))))
                northingEnd = northingStart + (vectorDistance * (cos(radians(j * 5))))
                #
                # Prepare geometry
                array = arcpy.Array([arcpy.Point(eastingStart, northingStart),
                                     arcpy.Point(eastingEnd, northingEnd)])
                polyline = arcpy.Polyline(array)
                #
                # Write geometry & attribution
                # i = current FetchVectorID, j * 5 = bearing, polyline is the coordinate pairs
                cursor = arcpy.da.InsertCursor(fetchVectors, (fields))
                cursor.insertRow((i, (j * 5) , polyline,))

# Cleanup:
# Refresh the map view
arcpy.RefreshActiveView()

# Clear data
del cursor