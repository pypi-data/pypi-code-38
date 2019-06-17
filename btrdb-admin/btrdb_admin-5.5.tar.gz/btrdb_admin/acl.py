# btrdb_admin.acl
# Mixin module for ACL related tasks
#
# Not Implemented:
#   rpc GetIdentityProvider(GetIdentityProviderParams) returns (GetIdentityProviderResponse);
#   rpc SetIdentityProvider(SetIdentityProviderParams) returns (SetIdentityProviderResponse);
#   rpc GetPublicUser(GetPublicUserParams) returns (GetPublicUserResponse);

# Author:   PingThings
# Created:  Tue Dec 18 14:50:05 2018 -0500
#
# For license information, see LICENSE.txt
# ID: acl.py [] allen@pingthings.io $

"""
Mixin module for ACL related tasks
"""

##########################################################################
## Imports
##########################################################################

from btrdb_admin.grpcinterface import admin_pb2
from btrdb_admin.exceptions import BTRDBError, NotFoundError


##########################################################################
## Helpers
##########################################################################

def _group_to_dict(group):
    return {
        "name": group.name,
        "prefixes": [pref for pref in group.prefixes],
        "capabilities": [cap for cap in group.capabilities]
    }

def _user_to_dict(user):
    return {
        "username": user.username,
        "groups": [_group_to_dict(g) for g in user.groups],
    }

##########################################################################
## Classes
##########################################################################

class ACLMixin(object):
    """
    Mixin to provide access control list functionality for BTrDB Admin API
    """

    def get_all_users(self):
        """
        Returns a list of usernames for all BTrDB accounts

        gRPC call:
            rpc GetAllUsers(GetAllUsersParams) returns (GetAllUsersResponse)

        Returns
        -------
        list(str)
            list of strings representing users in the system

        """
        params = admin_pb2.GetAllUsersParams()
        response = self.client.GetAllUsers(params)
        return [user for user in response.user]


    def user_exists(self, username):
        """
        Determines whether a user account exists in BTrDB

        gRPC call:
            rpc UserExists(UserExistsParams) returns (UserExistsResponse)

        Parameters
        ----------
        username: str
            username for account

        Returns
        -------
        bool : whether the user exists

        """
        params = admin_pb2.UserExistsParams(username=username)
        response = self.client.UserExists(params)
        if response.error.code != 0:
            raise BTRDBError()
        return response.exists


    def create_user(self, username, password):
        """
        Creates a new user in BTrDB

        gRPC call:
            rpc CreateUser(CreateUserParams) returns (CreateUserResponse)

        Parameters
        ----------
        username: str
            username for new account
        password: str
            password for new account

        """
        params = admin_pb2.CreateUserParams(username=username, password=password)
        response = self.client.CreateUser(params)
        if response.error.code != 0:
            raise BTRDBError()


    def set_user_password(self, username, password):
        """
        Change the password for a user in BTrDB

        gRPC call:
            rpc SetUserPassword(SetUserPasswordParams) returns (SetUserPasswordResponse)

        Parameters
        ----------
        username: str
            username for account
        password: str
            password for account

        """
        params = admin_pb2.SetUserPasswordParams(username=username, password=password)
        response = self.client.SetUserPassword(params)
        if response.error.code != 0:
            raise BTRDBError()


    def get_api_key(self, username):
        """
        Retrieve a user's API key from BTrDB

        gRPC call:
            rpc GetAPIKey(GetAPIKeyParams) returns (GetAPIKeyResponse)

        Parameters
        ----------
        username: str
            username for account

        """
        params = admin_pb2.GetAPIKeyParams(username=username)
        response = self.client.GetAPIKey(params)
        if response.error.code != 0:
            raise BTRDBError()

        return response.apikey


    def reset_api_key(self, username):
        """
        Reset and return a user's API key from BTrDB

        gRPC call:
            rpc ResetAPIKey(ResetAPIKeyParams) returns (ResetAPIKeyResponse)

        Parameters
        ----------
        username: str
            username for account

        """
        params = admin_pb2.ResetAPIKeyParams(username=username)
        response = self.client.ResetAPIKey(params)
        if response.error.code != 0:
            raise BTRDBError()

        return response.apikey


    def delete_user(self, username):
        """
        Delete a user from BTrDB

        gRPC call:
            rpc DeleteUser(DeleteUserParams) returns (DeleteUserResponse)

        Parameters
        ----------
        username: str
            username for account to delete

        """
        params = admin_pb2.DeleteUserParams(username=username)
        response = self.client.DeleteUser(params)
        if response.error.code != 0:
            raise BTRDBError()


    def authenticate_user_by_key(self, apikey):
        """
        Delete a user from BTrDB

        gRPC call:
            rpc AuthenticateUserByKey(AuthenticateUserByKeyParams) returns (AuthenticateUserByKeyResponse)

        Parameters
        ----------
        apikey: str
            apikey for an account

        """
        params = admin_pb2.AuthenticateUserByKeyParams(apikey=apikey)
        response = self.client.AuthenticateUserByKey(params)
        if response.error.code != 0:
            raise BTRDBError()

        return response.user


    def authenticate_user(self, username, password):
        """
        Delete a user from BTrDB

        gRPC call:
            rpc AuthenticateUser(AuthenticateUserParams) returns (AuthenticateUserResponse)

        Parameters
        ----------
        username: str
            username for account
        password: str
            password for account

        """
        params = admin_pb2.AuthenticateUserParams(username=username, password=password)
        response = self.client.AuthenticateUser(params)
        if response.error.code != 0:
            raise BTRDBError()

        return response.user


    def get_all_groups(self):
        """
        Delete a user from BTrDB

        gRPC call:
            rpc GetAllGroups(GetAllGroupsParams) returns (GetAllGroupsResponse)

        Returns
        -------
        list(str)
            A list of group names

        """
        params = admin_pb2.GetAllGroupsParams()
        response = self.client.GetAllGroups(params)
        if response.error.code != 0:
            raise BTRDBError()

        return [group for group in response.group]



    def get_group(self, name):
        """
        Retreive group details from BTrDB

        gRPC call:
            rpc GetGroup(GetGroupParams) returns (GetGroupResponse)

        Parameters
        ----------
        name: str
            name of the group

        Returns
        -------
        dict
            a dictionary representing the group

        """
        params = admin_pb2.GetGroupParams(name=name)
        response = self.client.GetGroup(params)

        if response.error.code == 445:
            raise NotFoundError()

        if response.error.code != 0:
            raise BTRDBError()

        return _group_to_dict(response.group)


    def get_builtin_user(self, username):
        """
        Retreive group details from BTrDB

        gRPC call:
            rpc GetBuiltinUser(GetBuiltinUserParams) returns (GetBuiltinUserResponse)

        Parameters
        ----------
        username: str
            username of the user

        Returns
        -------
        dict
            a dictionary representing the user

        """
        params = admin_pb2.GetBuiltinUserParams(username=username)
        response = self.client.GetBuiltinUser(params)
        if response.error.code != 0:
            raise BTRDBError()

        return _user_to_dict(response.user)


    def add_user_to_group(self, username, group):
        """
        Adds a user to a group

        gRPC call:
            rpc AddUserToGroup(AddUserToGroupParams) returns (AddUserToGroupResponse)

        Parameters
        ----------
        username: str
            username of the user
        group: str
            name of the group

        """
        params = admin_pb2.AddUserToGroupParams(username=username, group=group)
        response = self.client.AddUserToGroup(params)
        if response.error.code != 0:
            raise BTRDBError()


    def remove_user_from_group(self, username, group):
        """
        Removes a user from a group

        gRPC call:
            rpc RemoveUserFromGroup(RemoveUserFromGroupParams) returns (RemoveUserFromGroupResponse)

        Parameters
        ----------
        username: str
            username of the user
        group: str
            name of the group

        """
        params = admin_pb2.RemoveUserFromGroupParams(username=username, group=group)
        response = self.client.RemoveUserFromGroup(params)
        if response.error.code != 0:
            raise BTRDBError()


    def set_group_prefixes(self, group, prefixes):
        """
        Removes a user from a group

        gRPC call:
            rpc SetGroupPrefixes(SetGroupPrefixesParams) returns (SetGroupPrefixesResponse)

        Parameters
        ----------
        group: str
            name of the group
        prefixes: list(str)
            list of strings representing the group prefixes

        """
        params = admin_pb2.SetGroupPrefixesParams(group=group, prefixes=prefixes)
        response = self.client.SetGroupPrefixes(params)
        if response.error.code != 0:
            raise BTRDBError()


    def set_group_capabilities(self, group, capabilities):
        """
        Replaces group capabilities

        gRPC call:
            rpc SetGroupCapabilities(SetGroupCapabilitiesParams) returns (SetGroupCapabilitiesResponse)

        Parameters
        ----------
        group: str
            name of the group
        capabilities: list(?)
            list of ? representing the group capabilities

        """
        params = admin_pb2.SetGroupCapabilitiesParams(group=group, capabilities=capabilities)
        response = self.client.SetGroupCapabilities(params)
        if response.error.code != 0:
            raise BTRDBError()


    def create_group(self, name):
        """
        Creates a new group in BTrDB

        gRPC call:
            rpc AddGroup(AddGroupParams) returns (AddGroupResponse)

        Parameters
        ----------
        name: str
            name of the name

        """
        params = admin_pb2.AddGroupParams(name=name)
        response = self.client.AddGroup(params)
        if response.error.code != 0:
            raise BTRDBError()



    def delete_group(self, name):
        """
        Deletes a group in BTrDB

        gRPC call:
            rpc DeleteGroup(DeleteGroupParams) returns (DeleteGroupResponse)

        Parameters
        ----------
        name: str
            name of the name

        """
        params = admin_pb2.DeleteGroupParams(name=name)
        response = self.client.DeleteGroup(params)
        if response.error.code != 0:
            raise BTRDBError()
