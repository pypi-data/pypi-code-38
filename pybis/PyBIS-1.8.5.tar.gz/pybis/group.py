from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .utils import VERBOSE, extract_permid, extract_nested_permid,format_timestamp
from .things import Things
from pandas import DataFrame

class Group(OpenBisObject):
    """ Managing openBIS authorization groups
    """
    
    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'AuthorizationGroup')

        if data is not None:
            self.a(data)
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __dir__(self):
        return [
            'code','description','users','roleAssignments',
            'get_users()', 'set_users()', 'add_users()', 'del_users()',
            'get_roles()', 'assign_role()', 'revoke_role(techId)'
        ]

    def get_persons(self):
        """ Returns a Things object wich contains all Persons (Users)
        that belong to this group.
        """

        columns = ['permId', 'userId', 'firstName', 'lastName', 'email', 'space', 'registrationDate', 'active']
        persons = DataFrame(self._users)
        if len(persons) == 0:
            persons = DataFrame(columns=columns)
        persons['permId'] = persons['permId'].map(extract_permid)
        persons['registrationDate'] = persons['registrationDate'].map(format_timestamp)
        persons['space'] = persons['space'].map(extract_nested_permid)
        p = Things(
            self.openbis, entity='person', 
            df=persons[columns],
            identifier_name='permId'
        )
        return p

    get_users = get_persons  # Alias
    get_members = get_persons  # Alias


    def get_roles(self, **search_args):
        """ Get all roles that are assigned to this group.
        Provide additional search arguments to refine your search.

        Usage::
            group.get_roles()
            group.get_roles(space='TEST_SPACE')
        """
        return self.openbis.get_role_assignments(group=self, **search_args)

    def assign_role(self, role, **kwargs):
        """ Assign a role to this group. If no additional attribute is provided,
        roleLevel will default to INSTANCE. If a space attribute is provided,
        the roleLevel will be SPACE. If a project attribute is provided,
        roleLevel will be PROJECT.

        Usage::
            group.assign_role(role='ADMIN')
            group.assign_role(role='ADMIN', space='TEST_SPACE')

        """

        try:
            self.openbis.assign_role(role=role, group=self, **kwargs)
            if VERBOSE:
                print(
                    "Role {} successfully assigned to group {}".format(role, self.code)
                ) 
        except ValueError as e:
            if 'exists' in str(e):
                if VERBOSE:
                    print(
                        "Role {} already assigned to group {}".format(role, self.code)
                    )
            else:
                raise ValueError(str(e))


    def revoke_role(self, role, space=None, project=None, reason='no reason specified'):
        """ Revoke a role from this group. 
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
                    print("Role has already been revoked from group {}".format(role, self.code))
                return
            techId = roles.query(querystr)['techId'].values[0]

        # finally delete the role assignment
        ra = self.openbis.get_role_assignment(techId)
        ra.delete(reason)
        if VERBOSE:
            print(
                "Role {} successfully revoked from group {}".format(role, self.code)
            ) 
        return


    def _repr_html_(self):
        """ creates a nice table in Jupyter notebooks when the object itself displayed
        """
        def nvl(val, string=''):
            if val is None:
                return string
            return val

        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self._allowed_attrs:
            if attr in ['users','roleAssignments']:
                continue
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, nvl(getattr(self, attr, ''), '')
            )

        html += """
            </tbody>
            </table>
        """

        if getattr(self, '_users') is not None:
            html += """
                <br/>
                <b>Users</b>
                <table border="1" class="dataframe">
                <thead>
                    <tr style="text-align: right;">
                    <th>userId</th>
                    <th>FirstName</th>
                    <th>LastName</th>
                    <th>Email</th>
                    <th>Space</th>
                    <th>active</th>
                    </tr>
                </thead>
                <tbody>
            """
            for user in self._users:
                html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    user.get('userId'),
                    user.get('firstName'),
                    user.get('lastName'),
                    user.get('email'),
                    user.get('space').get('code') if user.get('space') is not None else '',
                    user.get('active'),
                )
            html += """
                </tbody>
                </table>
            """
        return html

    def delete(self, reason='unknown'):
        self.openbis.delete_entity(
            entity = "AuthorizationGroup",
            id = self.permId, 
            reason = reason
        )
        if VERBOSE:
            print("Authorization group {} successfully deleted".format(
                self.permId
            ))

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Group successfully created.")
            # re-fetch group from openBIS
            new_data = self.openbis.get_group(resp[0]['permId'], only_data=True)
            self._set_data(new_data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Group successfully updated.")
            # re-fetch group from openBIS
            new_data = self.openbis.get_group(self.permId, only_data=True)
            self._set_data(new_data)

