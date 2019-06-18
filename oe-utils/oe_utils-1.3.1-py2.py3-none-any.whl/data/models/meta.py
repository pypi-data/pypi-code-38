"""
Dit bestand bevat een OE Base Model dat in alle OE toepassingen kan worden gebruikt. Het voordeel van een generieke
Base is dat we op deze werkwijze per toepassing 1 zelfde Base kunnen gebruiken voor al de aanwezige Models.
Dit omvat zowel Models van de applicatie zelf, als de Models uit libraries zoals oe_utils en oe_geoutils.

Hier kan eveneens de nodige generieke metadata aan ons Base Model worden meegegeven.
Hiervoor kan sqlalchemy.schema.MetaData worden gebruikt
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
