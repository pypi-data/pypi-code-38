from ms_sdk.Resourses import Resource


class WishListItemsResource(Resource):
    """
    Class WishListItemsResource
    :method WishListItem get(int id):
    :method WishListItem first():
    :method WishListItem[] all():
    :method WishListItem update(id, data):
    :method WishListItem create(data):
    """

    def getURI(self):
        return 'wishlistitems'