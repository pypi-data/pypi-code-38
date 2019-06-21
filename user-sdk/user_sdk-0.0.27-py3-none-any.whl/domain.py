from dataclasses import dataclass, asdict
from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import datetime


class CredentialType(Enum):
    USERNAME = "USERNAME"
    MOBILE = "MOBILE"
    OAUTH = "OAUTH"

    def __str__(self):
        return self.value


class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

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
    usual_departure_time: Optional[int] = None

    def to_dict(self):
        rv = {"location_name": self.location_name, "location": asdict(self.location)}

        if self.street_address:
            rv["street_address"] = self.street_address

        if self.usual_departure_time:
            rv["usual_departure_time"] = self.usual_departure_time

        return rv


@dataclass
class UserProfile:
    user_id: UUID
    name: str
    gender: Gender
    home_address: Address
    work_address: Address
    device_id: Optional[str] = None
    dob: Optional[datetime] = None
    email: Optional[str] = None
    img_url: Optional[str] = None
    push_notification_id: Optional[str] = None
    fb_access_token: Optional[str] = None
    platform: Optional[str] = None
    app_version: Optional[str] = None

    def to_dict(self):
        rv = {
            "id": str(self.user_id),
            "name": self.name,
            "gender": self.gender.name,
            "home_address": self.home_address.to_dict(),
            "work_address": self.work_address.to_dict(),
        }

        if self.dob:
            rv["dob"] = self.dob
        if self.email:
            rv["email"] = self.email
        if self.img_url:
            rv["img_url"] = self.img_url
        if self.push_notification_id:
            rv["push_notification_id"] = self.push_notification_id
        if self.device_id:
            rv["device_id"] = self.device_id
        if self.fb_access_token:
            rv["fb_access_token"] = self.fb_access_token
        if self.app_version:
            rv["app_version"] = self.app_version
        if self.platform:
            rv["platform"] = self.platform

        return rv


@dataclass
class Credential:
    id: UUID
    type: CredentialType
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
