# Copyright (c) 2019, Lars Wilhelmsen <lars@sral.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import httplib2
from cachetools import cached, TTLCache
from jwcrypto.jwk import JWKSet

from .discovery import discover_OP_information

# cache answer for 10 hours
# TODO pull cache ttl from config
@cached(cache=TTLCache(maxsize=128, ttl=6000))
def retrieve_jwks(OP_uri, httpFactory=None):
  """
  Retrieves the potential keys used to sign issued tokens from the OP.
  """
  http = None
  if httpFactory is not None and callable(httpFactory):
    http = httpFactory()
  else:
    http = httplib2.Http()
  
  disco = discover_OP_information(OP_uri, httpFactory)
  jwks_uri = disco['jwks_uri']
  
  _, content = http.request(jwks_uri)
  
  return JWKSet.from_json(content)