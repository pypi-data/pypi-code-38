from uuid import uuid4

import pytest
import responses

from user_sdk.user_service import UserService

user_service = UserService(
    authentication_url="http://dummy_authentication",
    profile_url="http://dummy_profile",
    authorization_url="http://dummy_authorization",
)


def test_dict_to_user():
    user = user_service._dict_to_user(user_dict)
    assert user.id == "b402e055-2884-43a1-9e33-dbfe67e62971"
    assert 1 == len(user.identities)


def test_dict_to_user_profile():
    user_profile = user_service._dict_to_user_profile(user_profile_dict)
    assert user_profile.name == "sample_name"
    assert "sample_work_address" == user_profile.work_address.location_name
    assert "sample_home_address" == user_profile.home_address.location_name
    assert "MALE" == user_profile.gender.name


def test_dict_to_user_profile_for_incomplete_user_profile():
    user_profile = user_service._dict_to_user_profile(incomplete_user_profile_dict)
    assert user_profile.name is None
    assert user_profile.work_address is None
    assert "sample_home_address" == user_profile.home_address.location_name
    assert user_profile.gender is None


def test_dict_to_session():
    session = user_service._dict_to_session(session_response)
    assert session.user.id == "30944af3-dfe7-45e5-a860-31ac4a18bc69"
    assert (
        session.id
        == "FEZRHOQLBALFB4QE3S3LLN52RROVR6PTC4JQT44WFFZWNC4QKT3JTFQJX2E2LAKXGCFQD4BN63TTEIADCFKDFYAI4RCJRAHL7JCWHYY"
    )


@responses.activate
def test_get_user_from_session_throws_rte_if_non_ok_response():
    session_id = str(uuid4())
    responses.add(
        responses.GET,
        f"http://dummy_authentication/api/v1/sessions/{session_id}",
        status=500,
        json=dict(key="value"),
    )
    with pytest.raises(RuntimeError) as exc_info:
        user_service.get_user_from_session(session_id)

    assert exc_info.value.args == RuntimeError(500, '{"key": "value"}').args


user_dict = {
    "created_at": "2018-10-18T09:05:59.334113",
    "credentials": [
        {
            "created-at": "2018-10-18 09:05:59.334075",
            "id": "d417ad09-d5ae-4a72-9060-419308e6756d",
            "identity": "+917042329887",
            "identity_type": "MOBILE",
            "updated-at": "2018-10-18 09:05:59.334091",
            "verified": True,
        }
    ],
    "id": "b402e055-2884-43a1-9e33-dbfe67e62971",
    "suspended": False,
    "updated_at": "2018-10-18T09:05:59.334119",
}

user_profile_dict = {
    "created_at": "2018-10-18T13:04:55.643673",
    "gender": "MALE",
    "home_address": {
        "location": {"lat": 28.88, "lng": 77.33},
        "location_name": "sample_home_address",
    },
    "id": "f77971a6-3a7f-4475-81b6-2fe9e085f0bc",
    "name": "sample_name",
    "updated_at": "2018-10-18T13:04:55.643673",
    "work_address": {
        "location": {"lat": 27.88, "lng": 76.33},
        "location_name": "sample_work_address",
    },
}

incomplete_user_profile_dict = {
    "created_at": "2018-10-18T13:04:55.643673",
    "home_address": {
        "location": {"lat": 28.88, "lng": 77.33},
        "location_name": "sample_home_address",
    },
    "id": "f77971a6-3a7f-4475-81b6-2fe9e085f0bc",
    "updated_at": "2018-10-18T13:04:55.643673",
}
session_response = {
    "id": "fd335403-83bc-4eb5-b42e-6eb6674f4537",
    "created_at": "2018-10-21T13:52:50.208448",
    "updated_at": "2018-10-21T13:52:50.208457",
    "session_id": "FEZRHOQLBALFB4QE3S3LLN52RROVR6PTC4JQT44WFFZWNC4QKT3JTFQJX2E2LAKXGCFQD4BN63TTEIADCFKDFYAI4RCJRAHL7JCWHYY",
    "user": {
        "id": "30944af3-dfe7-45e5-a860-31ac4a18bc69",
        "created_at": "2018-10-21T07:41:36.034161",
        "updated_at": "2018-10-21T07:41:36.034184",
        "suspended": False,
        "credentials": [
            {
                "id": "c28ee1f5-8632-42e4-97a3-bbd60893bb7b",
                "created-at": "2018-10-21 07:41:36.023701",
                "updated-at": "2018-10-21 07:41:36.032386",
                "identity": "+917042329887",
                "identity_type": "MOBILE",
                "verified": True,
            }
        ],
    },
    "credential": {
        "id": "c28ee1f5-8632-42e4-97a3-bbd60893bb7b",
        "created-at": "2018-10-21 07:41:36.023701",
        "updated-at": "2018-10-21 07:41:36.032386",
        "identity": "+917042329887",
        "identity_type": "MOBILE",
        "verified": True,
    },
}
