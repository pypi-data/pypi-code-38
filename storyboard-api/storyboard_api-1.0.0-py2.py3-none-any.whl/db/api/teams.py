# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sqlalchemy.orm import subqueryload
from wsme.exc import ClientSideError

from storyboard._i18n import _
from storyboard.common import exception as exc
from storyboard.db.api import base as api_base
from storyboard.db.api import projects
from storyboard.db.api import users
from storyboard.db import models


def _entity_get(id, session=None):
    if not session:
        session = api_base.get_session()
    query = session.query(models.Team)\
        .options(subqueryload(models.Team.users))\
        .filter_by(id=id)

    return query.first()


def team_get(team_id, session=None):
    return _entity_get(team_id, session=session)


def _team_build_query(project_id=None, **kwargs):
    query = api_base.model_query(models.Team)

    if project_id:
        query = query.join(models.Team.projects)
        query = query.filter(models.Project.id == project_id)

    query = api_base.apply_query_filters(query=query,
                                         model=models.Team,
                                         **kwargs)

    return query


def team_get_all(marker=None, offset=None, limit=None, sort_field=None,
                 sort_dir=None, project_id=None, **kwargs):
    query = _team_build_query(project_id, **kwargs)
    query = api_base.paginate_query(query=query,
                                    model=models.Team,
                                    limit=limit,
                                    sort_key=sort_field,
                                    marker=marker,
                                    offset=offset,
                                    sort_dir=sort_dir)
    return query.all()


def team_get_count(project_id=None, **kwargs):
    query = _team_build_query(project_id, **kwargs)
    return query.count()


def team_create(values):
    return api_base.entity_create(models.Team, values)


def team_update(team_id, values):
    return api_base.entity_update(models.Team, team_id,
                                  values)


def team_add_user(team_id, user_id):
    session = api_base.get_session()

    with session.begin(subtransactions=True):
        team = _entity_get(team_id, session)
        if team is None:
            raise exc.NotFound(_("Team %s not found") % team_id)

        user = users.user_get(user_id)
        if user is None:
            raise exc.NotFound(_("User %s not found") % user_id)

        if user_id in [u.id for u in team.users]:
            raise ClientSideError(_("The User %(user_id)d is already "
                                    "in Team %(team_id)d") %
                                  {'user_id': user_id, 'team_id': team_id})

        team.users.append(user)
        session.add(team)

    return team


def team_delete_user(team_id, user_id):
    session = api_base.get_session()

    with session.begin(subtransactions=True):
        team = _entity_get(team_id, session)
        if team is None:
            raise exc.NotFound(_("Team %s not found") % team_id)

        user = users.user_get(user_id)
        if user is None:
            raise exc.NotFound(_("User %s not found") % user_id)

        if user_id not in [u.id for u in team.users]:
            raise ClientSideError(_("The User %(user_id)d is not in "
                                    "Team %(team_id)d") %
                                  {'user_id': user_id, 'team_id': team_id})

        user_entry = [u for u in team.users if u.id == user_id][0]
        team.users.remove(user_entry)
        session.add(team)

    return team


def team_add_project(team_id, project_id):
    session = api_base.get_session()

    with session.begin(subtransactions=True):
        team = _entity_get(team_id, session)
        if team is None:
            raise exc.NotFound(_("Team %s not found") % team_id)

        project = projects.project_get(project_id)
        if project is None:
            raise exc.NotFound(_("Project %s not found") % project_id)

        if project_id in [p.id for p in team.projects]:
            raise ClientSideError(_("The Project %(user_id)d is already "
                                    "in Team %(team_id)d") %
                                  {'project_id': project_id,
                                   'team_id': team_id})

        team.projects.append(project)
        session.add(team)

    return team


def team_delete_project(team_id, project_id):
    session = api_base.get_session()

    with session.begin(subtransactions=True):
        team = _entity_get(team_id, session)
        if team is None:
            raise exc.NotFound(_("Team %s not found") % team_id)

        project = projects.project_get(project_id)
        if project is None:
            raise exc.NotFound(_("Project %s not found") % project_id)

        if project_id not in [p.id for p in team.projects]:
            raise ClientSideError(_("The Project %(user_id)d is not in "
                                    "Team %(team_id)d") %
                                  {'project_id': project_id,
                                   'team_id': team_id})

        project_entry = [p for p in team.projects if p.id == project_id][0]
        team.projects.remove(project_entry)
        session.add(team)

    return team


def team_delete(team_id):
    team = team_get(team_id)

    if not team:
        raise exc.NotFound(_('Team not found.'))

    if len(team.users) > 0:
        raise exc.NotEmpty(_('Team must be empty.'))

    api_base.entity_hard_delete(models.Team, team_id)
