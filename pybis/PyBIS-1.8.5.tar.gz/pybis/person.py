from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .utils import VERBOSE


class Person(OpenBisObject):
    """ managing openBIS persons
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Person' )

        if data is not None:
            self.a(data)
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])


    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return [
            'permId', 'userId', 'firstName', 'lastName', 'email',
            'registrator', 'registrationDate','space',
            'get_roles()', 'assign_role(role, space)', 'revoke_role(role)',
        ]


    def get_roles(self, **search_args):
        """ Get all roles that are assigned to this person.
        Provide additional search arguments to refine your search.

        Usage::
            person.get_roles()
            person.get_roles(space='TEST_SPACE')
        """
        return self.openbis.get_role_assignments(person=self, **search_args)


    def assign_role(self, role, **kwargs):
        try:
            self.openbis.assign_role(role=role, person=self, **kwargs)
            if VERBOSE:
                print(
                    "Role {} successfully assigned to person {}".format(role, self.userId)
                ) 
        except ValueError as e:
            if 'exists' in str(e):
                if VERBOSE:
                    print(
                        "Role {} already assigned to person {}".format(role, self.userId)
                    )
            else:
                raise ValueError(str(e))


    def revoke_role(self, role, space=None, project=None, reason='no reason specified'):
        """ Revoke a role from this person. 
        """

        techId = None
        if isinstance(role, int):
            techId = role
        else:
            query = { "role": role }
            if space is None:
                query['space'] = ''
            else:
                query['space'] = space.upper()

            if project is None:
                query['project'] = ''
            else:
                query['project'] = project.upper()

            # build a query string for dataframe
            querystr = " & ".join( 
                    '{} == "{}"'.format(key, value) for key, value in query.items()
                    )
            roles = self.get_roles().df
            if len(roles) == 0:
                if VERBOSE:
                    print("Role has already been revoked from person {}".format(role, self.code))
                return
            techId = roles.query(querystr)['techId'].values[0]

        # finally delete the role assignment
        ra = self.openbis.get_role_assignment(techId)
        ra.delete(reason)
        if VERBOSE:
            print(
                "Role {} successfully revoked from person {}".format(role, self.code)
            ) 
        return


    def __str__(self):
        return "{} {}".format(self.get('firstName'), self.get('lastName'))

    def delete(self, reason):
        raise ValueError("Persons cannot be deleted")

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            # for new and updated objects, the parameter is
            # unfortunately called homeSpaceId, spaceId throws no error
            # but makes no change either
            if "spaceId" in request['params'][1][0]:
                request['params'][1][0]['homeSpaceId'] =  request['params'][1][0]['spaceId']
                del(request['params'][1][0]['spaceId'])
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Person successfully created.")
            new_person_data = self.openbis.get_person(resp[0]['permId'], only_data=True)
            self._set_data(new_person_data)
            return self

        else:
            request = self._up_attrs()
            # for new and updated objects, the parameter is
            # unfortunately called homeSpaceId, spaceId throws no error
            # but makes no change either
            if "spaceId" in request['params'][1][0]:
                request['params'][1][0]['homeSpaceId'] =  request['params'][1][0]['spaceId']
                del(request['params'][1][0]['spaceId'])
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Person successfully updated.")
            new_person_data = self.openbis.get_person(self.permId, only_data=True)
            self._set_data(new_person_data)

