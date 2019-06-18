import time
from ms_sdk.Entities.User import User
from ms_sdk.Lib.Filters.FilterOperators import FilterOperators
from ms_sdk.Lib.Helpers.Guid import Guid
from ms_sdk.Lib.Specifications.Users.IsUserEmail import IsUserEmail
from ms_sdk.Lib.Specifications.Users.IsUserSubscriber import IsUserSubscriber
from ms_sdk.Resourses import Resource


class UsersResource(Resource):
    """
    Class UsersResource
    :method User get(int id):
    :method User first():
    :method User[] all():
    :method User update(id, data):
    :method User create(data):
    """

    def getURI(self):
        return 'users'

    def subscribe(self, email, name=''):
        """
        Subscribe user
        :param email:
        :param name:
        :return User|None:
        """
        userList = self.filter(IsUserEmail(email).asFilter()).limit(1).all()

        user = userList or User({
            'email': email,
            'name': name,
            'guid': Guid.Generate(),
            'isSubscriber': 1
        })

        if IsUserSubscriber().isSatisfiedBy(user):
            return None

        if user.id:
            return self.update(user.id, {'isSubscriber': 1})

        return self.create(user)

    def unsubscribe(self, guid):
        """
        Unsubscribe user
        :param guid:
        :return User|None:
        """
        userList = self.fields(['isSubscriber']).filter({'guid': {FilterOperators.EQUAL: guid}}).limit().all()

        try:
            return self.update(userList.id, {'isSubscriber': 0})
        except:
            return None

    def getWishList(self, userId):
        """
        :param userId:
        :return WishListItem[]:
        """
        response = self.handler.handle('GET', False, 'wishlist/' + str(userId))
        return self.make(response, True)

    def addToWishList(self, userId, productId):
        """
        :param userId:
        :param productId:
        :return WishListItem:
        """
        return self.client.wishListItems().create({
            'userId': userId,
            'productId': productId,
            'createDate': time.strftime('%Y-%m-%d %H:%M:%S'),
        })

    def removeFromWishList(self, userId, productId):
        """
        :param userId:
        :param productId:
        :rtype bool:
        :raises EntityNotFoundException:
        """
        item = self.client.wishListItems().filter({
            'userId': {'e': userId},
            'productId': {'e': productId}
        }).first()

        if item:
            return self.client.wishListItems().delete(item.id)
