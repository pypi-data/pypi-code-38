"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
from cortex_client.utils import get_cortex_profile

DEFAULT_API_ENDPOINT = 'https://api.cortex.insights.ai'


class CortexEnv:
    """
    Sets environment variables for Cortex.
    """
    def __init__(self):
        profile = get_cortex_profile()

        self.api_endpoint = os.getenv('CORTEX_URI', profile.get('url'))
        self.token = os.getenv('CORTEX_TOKEN', profile.get('token'))
        self.account = os.getenv('CORTEX_ACCOUNT', profile.get('account'))
        self.username = os.getenv('CORTEX_USERNAME', profile.get('username'))
        self.password = os.getenv('CORTEX_PASSWORD')
