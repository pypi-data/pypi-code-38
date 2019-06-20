import enum
from dataclasses import dataclass, asdict
from enum import Enum
from http import HTTPStatus
from uuid import UUID
from typing import Optional
from datetime import datetime
from user_sdk.log import log

import requests

from user_sdk.error import (UserAuthenticationError,
                            NoSuchUser,
                            ProfileCreationError,
                            ProfileUpdateError,
                            UserCreationFailed,
                            NoSuchProfile,
                            OTPSendFailure,
                            UserAlreadyExists,
                            InvalidOTPError,
                            ProfileAlreadyExists)


class CredentialType(Enum):
    EMAIL = 'EMAIL'
    MOBILE = 'MOBILE'
    OAUTH = 'OAUTH'

    def __str__(self):
        return self.value


class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'

    def __str__(self):
        return self.value


@dataclass
class Location:
    lat: float
    lng: float


@dataclass
class Address:
    location_name: str
    location: Location
    street_address: Optional[str] = None

    def to_dict(self):
        rv = {
            'location_name': self.location_name,
            'location': asdict(self.location)
        }

        if self.street_address:
            rv['street_address'] = self.street_address

        return rv


@dataclass
class UserProfile:
    name: str
    gender: Gender
    home_address: Address
    work_address: Address
    dob: Optional[datetime] = None
    email: Optional[str] = None
    push_notification_id: Optional[str] = None

    def to_dict(self):
        rv = {
            'name': self.name,
            'gender': self.gender.name,
            'home_address': self.home_address.to_dict(),
            'work_address': self.work_address.to_dict()
        }

        if self.dob:
            rv['dob'] = self.dob
        if self.email:
            rv['email'] = self.email
        if self.push_notification_id:
            rv['push_notification_id'] = self.push_notification_id

        return rv


@dataclass
class Credential:
    id: UUID
    identity: str
    verified: bool


@dataclass
class User:
    id: UUID
    identities: [Credential]


@dataclass
class Session:
    id: str
    user: User


class UserService:
    def __init__(self, auth_url, profile_url):
        self._auth_url, self._profile_url = auth_url, profile_url

    def login_with_email(self, email: str, password: str) -> Session:
        return self._login(cred_type=CredentialType.EMAIL, identity=email, password=password)

    def login_with_mobile(self, phone_number: str, otp: str) -> Session:
        return self._login(cred_type=CredentialType.MOBILE, identity=phone_number, otp=otp)

    def login_with_oauth(self, id_token: str) -> Session:
        return self._login(cred_type=CredentialType.OAUTH, identity=id_token)

    def _login(self, cred_type, identity, password=None, otp=None) -> Session:
        body = {'identity': identity, 'credential_type': str(cred_type)}
        if cred_type == CredentialType.EMAIL:
            body['password'] = password
        elif cred_type == CredentialType.MOBILE:
            body['otp'] = otp
        request_url = f'{self._auth_url}/api/v1/sign_in'
        response = requests.post(request_url, json=body)
        log(message='login', request_url=request_url, request_body=body, status_code=response.status_code, response=response.text)
        if response.status_code == HTTPStatus.CREATED:
            return self._dict_to_session(response.json()['data'])
        if response.status_code == HTTPStatus.BAD_REQUEST:
            error_type = response.json()['error']['type']
            if error_type == 'INVALID_PASSWORD' or error_type == 'INVALID_OTP':
                raise InvalidOTPError
        raise UserAuthenticationError(response.json()['error'])

    def get_user_from_session(self, session_id: str) -> Session:
        response = requests.get(f'{self._auth_url}/api/v1/sessions/{session_id}')
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_session(response.json()['data'])
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser
        raise RuntimeError(response.status_code, response.json())

    def create_profile(self, user_id: UUID, profile: UserProfile) -> UserProfile:
        profile_dict = profile.to_dict()
        body = {
            'user_id': str(user_id),
            'profile': profile_dict,
        }
        request_url = f'{self._profile_url}/api/v1/profiles'
        response = requests.post(request_url, json=body)
        log(message='create_profile', request_url=request_url, request_body=body,
            status_code=response.status_code, response=response.text)

        if response.status_code == HTTPStatus.CREATED:
            return self._dict_to_user_profile(response.json().get('data'))
        if response.status_code == HTTPStatus.CONFLICT:
            raise ProfileAlreadyExists()
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileCreationError(response.json().get('error'))
        raise RuntimeError(response.status_code, response.json())

    def update_profile(self, user_id: str, profile: dict) -> UserProfile:
        request_url = f'{self._profile_url}/api/v1/profiles/{user_id}'
        response = requests.patch(url=request_url, json=profile)
        log(message='update_profile', request_url=request_url,
            status_code=response.status_code, response=response.text, request_body=profile)
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user_profile(response.json().get('data'))
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileUpdateError(response.json().get('error'))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchProfile
        raise RuntimeError(response.status_code, response.json())

    def get_user_profile(self, id: str) -> UserProfile:
        request_url = f'{self._profile_url}/api/v1/profiles/%s' % str(id)
        response = requests.get(request_url)
        log(message='get_user_profile', request_url=request_url,
            status_code=response.status_code, response=response.text)
        if response.status_code == HTTPStatus.OK:
            return self._dict_to_user_profile(response.json().get('data'))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchProfile
        raise RuntimeError(response.status_code, response.json())


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
            raise ValueError(f'Invalid credential_type {credential_type})')

        body = {
            'credential_type': credential_type.name,
            'identity': str(identity),
            'requires_verification': requires_verification
        }

        if password:
            body['password'] = password

        request_url = f'{self._auth_url}/api/v1/users'

        response = requests.post(request_url, json=body)
        log(message='create_user', request_url=request_url,
            status_code=response.status_code, response=response.text, request_body=body)

        if response.status_code == HTTPStatus.CREATED:
            return self._dict_to_user(response.json().get('data'))
        if response.status_code == HTTPStatus.CONFLICT:
            raise UserAlreadyExists
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise UserCreationFailed(response.json().get('error'))
        else:
            raise OTPSendFailure(response.json().get('error'))

    def generate_otp(self, credential_type: str, identity):
        cred_type = CredentialType(credential_type)
        body = {
            'credential_type': cred_type.name,
            'identity': identity
        }
        request_url = f'{self._auth_url}/api/v1/sessions/otp'
        response = requests.post(request_url, json= body)
        log(message='generate_otp', request_url=request_url,
            status_code=response.status_code, response=response.text, request_body=body)
        if response.status_code != HTTPStatus.ACCEPTED:
            raise OTPSendFailure

    def get_by_email(self, email: str)-> User:
        response = requests.get(f'{self._auth_url}/api/v1/users/by_identity/%s' % email)
        if response.status_code == 200:
            return self._dict_to_user(response.json().get('data'))
        # Todo: handle failure cases

    def get_by_mobile_number(self, mobile_number: str)-> User:
        response = requests.get(f'{self._auth_url}/api/v1/users/by_identity/%s' % mobile_number)
        if response.status_code == 200:
            return self._dict_to_user(response.json().get('data'))
        # Todo: handle failure cases

    def _dict_to_session(self, param) -> Session:
        user = self._dict_to_user(param.get('user'))
        return Session(param.get('session_id'), user=user)

    def _dict_to_user(self, param) -> User:
        def dict_to_cred(cred_dict):
            return Credential(id=cred_dict['id'], identity=cred_dict['identity'], verified=cred_dict['verified'])

        return User(
            id=param['id'],
            identities=[dict_to_cred(cred) for cred in param['credentials']],
        )

    def _dict_to_user_profile(self, param) -> UserProfile:
        def dict_to_address(address_dict):
            return Address(location=Location(address_dict['location']['lat'], address_dict['location']['lng']),
                           location_name=address_dict['location_name'],
                           street_address=address_dict.get('street_address'))

        profile = UserProfile(name=param['name'], gender=Gender(param['gender']),
                              home_address=dict_to_address(param['home_address']),
                              work_address=dict_to_address(param['work_address']),
                              email=param.get('email'), push_notification_id=param.get('gcmId'))
        dob = param.get('dob')
        if dob:
            profile.dob = datetime.fromisoformat(dob)
        return profile
