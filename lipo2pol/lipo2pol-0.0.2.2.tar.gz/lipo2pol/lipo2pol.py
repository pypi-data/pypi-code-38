# Convert LineString OSM data to Polygon with real road width

# Import required library
import argparse
import geopandas as gpd
import os
import sys

# Define parser argument for input and output files
parser = argparse.ArgumentParser(description='Convert Point or LineString OSM Data to Polygon')
parser.add_argument("input",type=str, help="Input file that contain LineString or Point Geojson data")
#parser.add_argument("--type", help="Convert object type (point, linestring or both point and linestring object)", default='both')
parser.add_argument("--output", help="Output file Path/Name that contain converted Geojson data ", default='output.geojson')
args = parser.parse_args()

# Assign input file name to input variable
input = args.input

# Assign object type to type variable
#type = args.type

# Assign output file name to output variable
output = args.output

def getRoadTypeandWidth(road_type):
    if road_type == 'motorway':
        highway_attributes = {
            "lanes": 4,
            "lane_width": 3.75,
            "left_hard_shoulder_width": 0.75,
            "right_hard_shoulder_width": 3.0,
        }
        road_total_width = highway_attributes['lanes'] \
                         * highway_attributes['lane_width'] \
                         + highway_attributes['left_hard_shoulder_width'] \
                         + highway_attributes['right_hard_shoulder_width']
        print('Road type: motorway ')
        print('Road total width : ', road_total_width)
        print('--------------------------------------')
        return highway_attributes, road_total_width

    elif road_type == 'trunk':
        highway_attributes = {
            "lanes": 3,
            "lane_width": 3.75,
            "left_hard_shoulder_width": 0.75,
            "right_hard_shoulder_width": 3.0,
        }
        road_total_width = highway_attributes['lanes'] \
                         * highway_attributes['lane_width'] \
                         + highway_attributes['left_hard_shoulder_width'] \
                         + highway_attributes['right_hard_shoulder_width']
        print('Road type: trunk ')
        print('Road total width : ', road_total_width)
        print('--------------------------------------')
        return highway_attributes, road_total_width

    elif road_type == 'primary':
        highway_attributes = {
            "lanes": 2,
            "lane_width": 3.75,
            "left_hard_shoulder_width": 0.50,
            "right_hard_shoulder_width": 1.5,
        }
        road_total_width = highway_attributes['lanes'] \
                         * highway_attributes['lane_width'] \
                         + highway_attributes['left_hard_shoulder_width'] \
                         + highway_attributes['right_hard_shoulder_width']
        print('Road type: primary ')
        print('Road total width : ', road_total_width)
        print('--------------------------------------')
        return highway_attributes, road_total_width

    elif road_type == 'secondary':
        highway_attributes = {
            "lanes": 1,
            "lane_width": 3.50,
            "left_hard_shoulder_width": 0.00,
            "right_hard_shoulder_width": 0.75,
        }
        road_total_width = highway_attributes['lanes'] \
                         * highway_attributes['lane_width'] \
                         + highway_attributes['left_hard_shoulder_width'] \
                         + highway_attributes['right_hard_shoulder_width']
        print('Road type: secondary ')
        print('Road total width : ', road_total_width)
        print('--------------------------------------')
        return highway_attributes, road_total_width

    elif road_type == 'tertiary':
        highway_attributes = {
            "lanes": 1,
            "lane_width": 3.50,
            "left_hard_shoulder_width": 0.00,
            "right_hard_shoulder_width": 0.75,
        }
        road_total_width = highway_attributes['lanes'] \
                         * highway_attributes['lane_width'] \
                         + highway_attributes['left_hard_shoulder_width'] \
                         + highway_attributes['right_hard_shoulder_width']
        print('Road type: tertiary ')
        print('Road total width : ', road_total_width)
        print('--------------------------------------')
        return highway_attributes, road_total_width

    else:
        highway_attributes = {
            "lanes": 1,
            "lane_width": 3.00,
            "left_hard_shoulder_width": 0.0,
            "right_hard_shoulder_width": 0.0,
        }
        road_total_width = highway_attributes['lanes'] \
                         * highway_attributes['lane_width'] \
                         + highway_attributes['left_hard_shoulder_width'] \
                         + highway_attributes['right_hard_shoulder_width']
        print('Road type: Other ')
        print('Road total width : ', road_total_width)
        print('--------------------------------------')
        return highway_attributes, road_total_width


def checkFile(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext != '.geojson':
        print('Invalid file type. Plase check your file.')
        return



def convertPolygon(inputFile, outputFile):
    # Read geojson data with geopandas
    checkFile(file_path=input)
    data = gpd.read_file(inputFile)

    # if you want to first 1000 row uncomment below line
    #data = data.head(1000)

    # get current Coordinate Reference Systems (CRS)
    current_crs = data.crs['init']
    print('Current Data CRS : ', current_crs)

    # Change CRSto EPSG 3395     # to calculate road with in meters
    data.to_crs(epsg=3395,inplace=True)

    # Call all rows one by one
    for index, row in data.iterrows():
        highway_attributes, road_total_width =  getRoadTypeandWidth(road_type=row['highway'])

        # if lanes has a valu assign this value to lanes cell
        if row['lanes'] != None:
            highway_attributes['lanes'] = row['lanes']
            print('Lanes value added', highway_attributes['lanes'])

        # if width:lanes (lanes' width) has a value assign this value to  width:lanes cell
        if row['width:lanes'] != None:
            highway_attributes['lane_width'] = row['width:lanes']
            print('width:lanes value added', highway_attributes['lane_width'])

        # Convert linestring to polygon using buffer method
        data.loc[index, 'geometry'] = row['geometry'].buffer(road_total_width)

    # Change CRS to old value
    data.to_crs(epsg=4326, inplace=True)

    # Write Polygon data to input file
    data.to_file(outputFile, driver='GeoJSON')

if __name__ == '__main__':
    convertPolygon(inputFile=args.input, outputFile = args.output)









