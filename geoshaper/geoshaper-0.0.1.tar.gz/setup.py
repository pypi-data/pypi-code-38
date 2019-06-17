from setuptools import setup

setup(
    name="geoshaper",
    version="0.0.1",
    description="An open source library to convert shape files to GeoJSON/TopoJSON",
    url="http://github.com/Datawheel/gepshaper",
    download_url="http://github.com/Datawheel/gepshaper/archive/0.0.1.tar.gz",
    author="Carlos Navarrete",
    author_email="cnavarreteliz@gmail.com",
    license="MIT",
    packages=["geoshaper"],
    install_requires=[
        "fiona",
        "geopandas",
        "pandas",
        "shapely",
        "topojson"
    ],
    dependency_links=[
      "shapely",
      "git+ssh://git@https://github.com/calvinmetcalf/topojson.py.git#egg=0.1.01.dev0",
    ],
    keywords=["geojson", "topojson", "shapes"],
    zip_safe=True
)