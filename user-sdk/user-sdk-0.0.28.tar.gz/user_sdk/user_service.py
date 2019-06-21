from datetime import datetime
from http import HTTPStatus
from typing import List
from uuid import UUID

import requests

from user_sdk.error import (
    InvalidOTPError,
    UserAuthenticationError,
    NoSuchUser,
    ProfileAlreadyExists,
    ProfileCreationError,
    ProfileUpdateError,
    NoSuchProfile,
    UserAlreadyExists,
    UserCreationFailed,
    OTPSendFailure,
    NoRoleFound,
    InvalidRoleRequest,
)
from user_sdk.log import log
from user_sdk.domain import (
    Session,
    CredentialType,
    UserProfile,
    User,
    Credential,
    Address,
    Location,
    Gender,
)


class UserService:
    def __init__(self, authentication_url, profile_url, authorization_url=None):
        self._authentication_url = authentication_url
        self._profile_url = profile_url
        self._authorization_url = authorization_url

    def login_with_username(self, username: str, password: str) -> Session:
        return self._login(
            cred_type=CredentialType.USERNAME, identity=username, password=password
        )

    def login_with_mobile(self, phone_number: str, otp: str) -> Session:
        return self._login(
            cred_type=CredentialType.MOBILE, identity=phone_number, otp=otp
        )

    def login_with_oauth(self, id_token: str) -> Session:
        return self._login(cred_type=CredentialType.OAUTH, identity=id_token)

    def _login(self, cred_type, identity, password=None, otp=None) -> Session:
        body = {"identity": identity, "credential_type": str(cred_type)}
        if cred_type == CredentialType.USERNAME:
            body["password"] = password
        elif cred_type == CredentialType.MOBILE:
            body["otp"] = otp
        request_url = f"{self._authentication_url}/api/v1/sign_in"
        response = requests.post(request_url, json=body)
        log(
            message="login",
            request_url=request_url,
            request_body=body,
            status_code=response.status_code,
            response=response.text,
        )
        if response.status_code == HTTPStatus.CREATED:
            return self._dict_to_session(response.json()["data"])
        if response.status_code == HTTPStatus.BAD_REQUEST:
            error_type = response.json()["error"]["type"]
            if error_type == "INVALID_PASSWORD" or error_type == "INVALID_OTP":
                raise InvalidOTPError
        raise UserAuthenticationError(response.json()["error"])

    def get_user_from_session(self, session_id: str) -> Session:
        response = requests.get(
            f"{self._authentication_url}/api/v1/sessions/{session_id}"
        )
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_session(response.json()["data"])
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def create_profile(self, profile: UserProfile) -> UserProfile:
        request_url = f"{self._profile_url}/api/v1/profiles"
        response = requests.post(request_url, json={"profile": profile.to_dict()})
        log(
            message="create_profile",
            request_url=request_url,
            request_body=profile.to_dict(),
            status_code=response.status_code,
            response=response.text,
        )

        if response.status_code == HTTPStatus.CREATED:
            return self._dict_to_user_profile(response.json()["data"])
        if response.status_code == HTTPStatus.CONFLICT:
            raise ProfileAlreadyExists()
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileCreationError(response.json().get("error"))

        self._raise_response_error(response)

    def update_profile(self, user_id: UUID, profile: dict) -> UserProfile:
        request_url = f"{self._profile_url}/api/v1/profiles/{user_id}"
        response = requests.patch(url=request_url, json=profile)
        log(
            message="update_profile",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=profile,
        )
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user_profile(response.json().get("data"))
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileUpdateError(response.json().get("error"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchProfile

        self._raise_response_error(response)

    def get_user_profile(self, id: UUID) -> UserProfile:
        request_url = f"{self._profile_url}/api/v1/profiles/%s" % str(id)
        response = requests.get(request_url)
        log(
            message="get_user_profile",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
        )
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user_profile(response.json().get("data"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchProfile

        self._raise_response_error(response)

    def get_user_profiles(self, ids: List[UUID]) -> List[UserProfile]:
        request_url = f"{self._profile_url}/api/v1/profiles/by_user_ids"
        response = requests.get(request_url, params={"ids": ",".join(map(str, ids))})
        log(
            message="get_user_profile",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
        )
        if response.status_code == HTTPStatus.OK:
            return [self._dict_to_user_profile(up) for up in response.json()["data"]]

        self._raise_response_error(response)

    def create_user(
        self,
        credential_type: str,
        identity: str,
        requires_verification: bool = True,
        password: str = None,
    ):
        try:
            credential_type = CredentialType[credential_type]
        except KeyError:
            raise ValueError(f"Invalid credential_type {credential_type})")

        body = {
            "credential_type": credential_type.name,
            "identity": str(identity),
            "requires_verification": requires_verification,
        }

        if password:
            body["password"] = password

        request_url = f"{self._authentication_url}/api/v1/users"

        response = requests.post(request_url, json=body)
        log(
            message="create_user",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=body,
        )

        if response.status_code == HTTPStatus.CREATED:
            return self._dict_to_user(response.json().get("data"))
        if response.status_code == HTTPStatus.CONFLICT:
            raise UserAlreadyExists
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise UserCreationFailed(response.json().get("error"))
        else:
            raise OTPSendFailure(response.json().get("error"))

    def generate_otp(self, credential_type: str, identity):
        cred_type = CredentialType(credential_type)
        body = {"credential_type": cred_type.name, "identity": identity}
        request_url = f"{self._authentication_url}/api/v1/sessions/otp"
        response = requests.post(request_url, json=body)
        log(
            message="generate_otp",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=body,
        )
        if response.status_code != HTTPStatus.ACCEPTED:
            raise OTPSendFailure

    def get_by_email(self, email: str) -> User:
        response = requests.get(
            f"{self._authentication_url}/api/v1/users/by_identity/%s" % email
        )
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user(response.json().get("data"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def get_by_mobile_number(self, mobile_number: str) -> User:
        response = requests.get(
            f"{self._authentication_url}/api/v1/users/by_identity/%s" % mobile_number
        )
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user(response.json().get("data"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def get_user(self, user_id: UUID) -> User:
        response = requests.get(f"{self._authentication_url}/api/v1/users/{user_id}")
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user(response.json()["data"])
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def get_user_role(self, email: str, panel: str) -> str:
        response = requests.get(
            f"{self._authorization_url}/api/v1/role",
            params=dict(email=email, panel=panel),
        )

        if response.status_code == HTTPStatus.OK:
            return response.json()["data"]["role"]

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoRoleFound("No role found for this email on panel")

        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise InvalidRoleRequest("Either Panel name or email format is invalid")

        self._raise_response_error(response)

    def _raise_response_error(self, response):
        raise RuntimeError(
            f"""
            Invalid response.

            Status code: {response.status_code}
            Text:

            {response.text}
        """
        )

    def _dict_to_session(self, param) -> Session:
        user = self._dict_to_user(param.get("user"))
        return Session(param.get("session_id"), user=user)

    def _dict_to_user(self, param) -> User:
        def dict_to_cred(cred_dict):
            return Credential(
                id=cred_dict["id"],
                type=CredentialType(cred_dict["identity_type"]),
                identity=cred_dict["identity"],
                verified=cred_dict["verified"],
            )

        return User(
            id=param["id"],
            identities=[dict_to_cred(cred) for cred in param["credentials"]],
        )

    def _dict_to_user_profile(self, param) -> UserProfile:
        def dict_to_address(address_dict):
            return Address(
                location=Location(
                    address_dict["location"]["lat"], address_dict["location"]["lng"]
                ),
                location_name=address_dict["location_name"],
                street_address=address_dict.get("street_address"),
                usual_departure_time=address_dict.get("usual_departure_time"),
            )

        profile = UserProfile(
            user_id=param["id"],
            name=param.get("name"),
            gender=Gender(param["gender"]) if param.get("gender") else None,
            home_address=dict_to_address(param["home_address"])
            if param.get("home_address")
            else None,
            work_address=dict_to_address(param["work_address"])
            if param.get("work_address")
            else None,
            email=param.get("email"),
            img_url=param.get("img_url"),
            push_notification_id=param.get("gcmId"),
            dob=datetime.fromisoformat(param["dob"]) if param.get("dob") else None,
            device_id=param.get("device_id"),
            fb_access_token=param.get("fb_access_token"),
            platform=param.get("platform"),
            app_version=param.get("app_version"),
        )
        return profile
