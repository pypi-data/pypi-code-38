from guillotina import configure
from guillotina.auth.validators import hash_password
from guillotina.event import notify
from guillotina.events import NewUserAdded
from guillotina.interfaces import IObjectAddedEvent
from guillotina_dbusers.content.users import IUser


@configure.subscriber(for_=(IUser, IObjectAddedEvent))
async def user_created(user, event):
    user.password = hash_password(user.password)

    # user has access to his own object by default
    # request = get_current_request()
    # roleperm = IPrincipalRoleManager(request.container)
    # roleperm.assign_role_to_principal('guillotina.Owner', user.id)

    await notify(NewUserAdded(user))
