import dataclasses
import enum

from typing import Optional


@dataclasses.dataclass(frozen=True)
class GoogleCloudProjectID:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(f'project_id must be a string, expect: {type(self.value)}')


@dataclasses.dataclass(frozen=True)
class GoogleCloudLocation:
    # TODO: リージョン一覧の取得は、 Google Compute Engine の API を利用して取得できるようにしたい
    #
    # Python 用の Google API Client Library を利用し、Compute Engine API の リージョン一覧
    # メソッドを使用することより、現在利用可能なリージョン一覧を取得できます。
    #
    # Google API Client Library for Python については、
    # 以下のリンク： [1] をご参照ください。
    #
    # また、Compute Engine API のリージョン一覧メソッドにつきましては、
    # 以下のリンク ：[2] をご参照ください。
    #
    # [1] https://developers.google.com/api-client-library/python/apis/compute/v1
    # [2] https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/compute_v1.regions.html#list # noqa: E501
    AVAILABLE_LOCATIONS = [
        'us-west1',  # オレゴン
        'us-west2',  # ロサンゼルス
        'us-central1',  # アイオワ
        'us-east1',  # サウスカロライナ
        'us-east4',  # 北バージニア
        'northamerica-northeast1',  # モントリオール
        'southamerica-east1',  # サンパウロ

        'europe-west1',  # ベルギー
        'europe-west2',  # ロンドン
        'europe-west3',  # フランクフルト
        'europe-west4',  # オランダ
        'europe-north1',  # フィンランド

        'asia-south1',  # ムンバイ
        'asia-southeast1',  # シンガポール
        'asia-east1',  # 台湾
        'asia-east2',  # 香港
        'asia-northeast1',  # 東京
        'australia-southeast1',  # シドニー
    ]
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(f'location must be a string, expect: {type(self.value)}')

        if self.value not in self.AVAILABLE_LOCATIONS:
            raise ValueError(f'Invalid value of {self.value} is not available locations.')


class ApplicationPlatform(enum.Enum):
    Local = 'local'
    GoogleAppEngine = 'google-app-engine'


@dataclasses.dataclass(frozen=True)
class ServiceAccountCredentialConfig:
    enabled: bool
    bucket_name: Optional[str] = None
    blob_path: Optional[str] = None

    def __post_init__(self):
        if not self.enabled:
            return

        if not isinstance(self.bucket_name, str):
            raise ValueError(f'bucket_name must be a string, expect: {type(self.bucket_name)}')

        if not isinstance(self.blob_path, str):
            raise ValueError(f'blob_path must be a string, expect: {type(self.blob_path)}')


# will be deprecated.
@dataclasses.dataclass(frozen=True)
class ServiceAccountCredentialPath:
    value: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.value, str) and not self.value.startswith('gs://'):
            raise ValueError(f'{self.__class__.__name__} must be starts with gs://')

    def credential_config(self) -> ServiceAccountCredentialConfig:
        if not isinstance(self.value, str):
            return ServiceAccountCredentialConfig(
                enabled=False
            )

        _, _, bucket_name, blob_path = self.value.split('/', 3)
        return ServiceAccountCredentialConfig(
            enabled=True,
            bucket_name=bucket_name,
            blob_path=blob_path,
        )


@dataclasses.dataclass(frozen=True)
class GumoConfiguration:
    google_cloud_project: GoogleCloudProjectID
    google_cloud_location: GoogleCloudLocation
    application_platform: ApplicationPlatform
    service_account_credential_config: ServiceAccountCredentialConfig  # will be deprecated

    @property
    def is_local(self) -> bool:
        return self.application_platform == self.application_platform.Local

    @property
    def is_google_app_engine(self) -> bool:
        return self.application_platform == self.application_platform.GoogleAppEngine
