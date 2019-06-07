# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

import collective.contentgroups


class ContentGroupsLayer(PloneSandboxLayer):
    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.contentgroups)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.contentgroups:default")


COLLECTIVE_CONTENT_GROUPS_FIXTURE = ContentGroupsLayer()


COLLECTIVE_CONTENT_GROUPS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CONTENT_GROUPS_FIXTURE,),
    name="ContentGroupsLayer:IntegrationTesting",
)


COLLECTIVE_CONTENT_GROUPS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CONTENT_GROUPS_FIXTURE,),
    name="ContentGroupsLayer:FunctionalTesting",
)


class ContentGroupsCreatedLayer(ContentGroupsLayer):
    """Layer that already has several groups already set up."""

    defaultBases = (COLLECTIVE_CONTENT_GROUPS_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.contentgroups.tests

        self.loadZCML(name="testing.zcml", package=collective.contentgroups.tests)

    def setUpPloneSite(self, portal):
        """Setup the Plone site with some groups.

        Create some standard groups and subgroups,
        and same for content groups, so we can compare.
        Let the groups ids start with the same character,
        so that we can check that both types can be found.
        """
        applyProfile(portal, "collective.contentgroups.tests:testing")
        # Create some standard groups.
        subcasual = api.group.create(groupname="subcasual", title="Sub Casual")
        casual = api.group.create(
            groupname="casual", title="Casual", roles=["Reader"], groups=["subcasual"]
        )
        # Create some content groups.  We need to be logged in for this.
        # Take over some lines from plone.app.contenttypes.testing
        # for creating a site owner and logging in.  I expected that the
        # site owner already existed, but apparently not.
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        content1 = api.content.create(
            container=portal, type="Group", id="content1", title="Content 1"
        )
        content2 = api.content.create(
            container=portal, type="Group", id="content2", title="Content 2"
        )
        # Create sub content groups.
        # Note that ids and title are different so that we can test the sort order.
        sub2a = api.content.create(
            container=portal, type="Group", id="sub2a", title="2A Sub Content"
        )
        sub2b = api.content.create(
            container=portal, type="Group", id="sub2b", title="2B Sub Content"
        )
        content_sub_of_standard = api.content.create(
            container=portal,
            type="Group",
            id="content_sub_of_standard",
            title="Content Sub of Standard",
        )
        content_sub_of_standard.users = ""
        logout()
        # Add the sub groups to their parent groups.
        api.group.add_user(group=casual, user=subcasual)
        # Ah, yes, we don't support this for content groups, because you have to go
        # through the content UI
        content2.users = "sub2a\nsub2b"
        # Let's also create a standard sub group in a content group:
        standard_sub_of_content = api.group.create(
            groupname="standard_sub_of_content",
            title="Standard Sub of Content 1",
            roles=["Reader"],
        )
        content1.users = "standard_sub_of_content"
        # and a content sub group in a standard group.
        api.group.add_user(group=casual, user=content_sub_of_standard)
        # Create some standard users and add them to groups.
        ann = api.user.create(
            email="ann@example.org",
            username="casual-ann",
            password="secret",
            properties={"title": "Ann Casual"},
        )
        api.group.add_user(group=casual, user=ann)
        bert = api.user.create(
            email="bert@example.org",
            username="subcasual-bert",
            password="secret",
            properties={"title": "Bert Sub Casual"},
        )
        api.group.add_user(group=subcasual, user=bert)
        corey = api.user.create(
            email="corey@example.org",
            username="content1-corey",
            password="secret",
            properties={"title": "Corey Content 1"},
        )
        content1.users += "\n{0}".format(corey.getUserId())
        donna = api.user.create(
            email="donna@example.org",
            username="content2-donna",
            password="secret",
            properties={"title": "Donna Content 2"},
        )
        content2.users += "\n{0}".format(donna.getUserId())
        eddy = api.user.create(
            email="eddy@example.org",
            username="sub2a-eddy",
            password="secret",
            properties={"title": "Eddy Sub 2A"},
        )
        sub2a.users = eddy.getUserId()
        fiona = api.user.create(
            email="fiona@example.org",
            username="sub2b-fiona",
            password="secret",
            properties={"title": "Fiona Sub 2B"},
        )
        sub2b.users = fiona.getUserId()
        # Add one user who is in all groups.
        general = api.user.create(
            email="general@example.org",
            username="general",
            password="secret",
            properties={"title": "General"},
        )
        for group in (casual, subcasual, standard_sub_of_content):
            api.group.add_user(group=group, user=general)
        for group in (content1, content2, sub2a, sub2b, content_sub_of_standard):
            group.users += "\n{0}".format(general.getUserId())
        # Add one user who is in all SUB groups.
        sub = api.user.create(
            email="sub@example.org",
            username="sub",
            password="secret",
            properties={"title": "Sub"},
        )
        for group in (subcasual, standard_sub_of_content):
            api.group.add_user(group=group, user=sub)
        for group in (sub2a, sub2b, content_sub_of_standard):
            group.users += "\n{0}".format(sub.getUserId())


COLLECTIVE_CONTENT_GROUPS_CREATED_FIXTURE = ContentGroupsCreatedLayer()


COLLECTIVE_CONTENT_GROUPS_CREATED_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CONTENT_GROUPS_CREATED_FIXTURE,),
    name="ContentGroupsCreatedLayer:IntegrationTesting",
)


COLLECTIVE_CONTENT_GROUPS_CREATED_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CONTENT_GROUPS_CREATED_FIXTURE,),
    name="ContentGroupsCreatedLayer:FunctionalTesting",
)
