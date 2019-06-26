from girder.models.item import Item as ItemModel
from girder.models.collection import Collection as CollectionModel
from girder.api.rest import boundHandler
from shapely.geometry import MultiPolygon, Polygon

BOUNDS_KEY = 'geometa_bounds'


@boundHandler
def itemAddedToCollection(self, event):
    item = ItemModel().load(event.info['file']['itemId'],
                            user=self.getCurrentUser())

    if item['baseParentType'] != 'collection':
        return
    collection = CollectionModel().load(item['baseParentId'],
                                        user=self.getCurrentUser())

    # Default to just bounding box of item itself
    newConvexHull = Polygon(*item['geometa']['bounds']['coordinates'])

    if BOUNDS_KEY in collection:
        oldConvexHull = Polygon(*collection[BOUNDS_KEY]['coordinates'])
        newConvexHull = MultiPolygon(
            polygons=[oldConvexHull, newConvexHull]).convex_hull

    collection[BOUNDS_KEY] = {
        'type': 'Polygon',
        'coordinates': [list(newConvexHull.exterior.coords)]
    }
    collection = CollectionModel().save(collection)


@boundHandler
def itemRemovedFromCollection(self, event):
    # More efficient way instead of whole recomputation?
    item = ItemModel().load(event.info['_id'],
                            user=self.getCurrentUser())

    if item['baseParentType'] != 'collection':
        return
    collection = CollectionModel().load(item['baseParentId'],
                                        user=self.getCurrentUser())

    # Default to just bounding box of item itself
    newConvexHull = computeCollectionConvexHull(
        collection,
        self.getCurrentUser()
    )

    collection[BOUNDS_KEY] = {
        'type': 'Polygon',
        'coordinates': [list(newConvexHull.exterior.coords)]
    }
    collection = CollectionModel().save(collection)


def computeCollectionConvexHull(collection, currentUser):
    docs = ItemModel().findWithPermissions(
        query={
            'baseParentId': collection['_id'],
            'geometa': {
                '$exists': True
            }
        },
        user=currentUser)

    convexHull = None
    collectionItems = [doc['geometa']['bounds'] for doc in docs]

    if collectionItems:
        polygons = [Polygon(*item['coordinates'])
                    for item in collectionItems]
        convexHull = MultiPolygon(polygons).convex_hull

    return convexHull
