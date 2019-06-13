# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

import copy


class OEFURI:

    def __init__(self):
        self.protocol = "tcp"
        self.coreURI = ""
        self.coreKey = ""
        self.namespaces = []
        self.agentKey = ""
        self.agentAlias = ""
        self.empty = True

    def toString(self) -> str:
        if self.empty:
            return ""
        return "{}://{}/{}/{}/{}/{}".format(self.protocol, self.coreURI, self.coreKey, "/".join(self.namespaces),
                                            self.agentKey, self.agentAlias)

    def __str__(self):
        return self.toString()

    def parse(self, uri: str):
        parts = uri.split("/")
        size = len(parts)
        if size < 7:
            #print("OEFURI parse failed! Invalid URI: '", uri, "'")
            return
        self.empty = False
        self.protocol = parts[0].replace(":", "")
        self.coreURI = parts[2]
        self.coreKey = parts[3]
        self.agentAlias = parts[size-1]
        self.agentKey = parts[size-2]
        for i in range(4, size-2):
            self.namespaces.append(parts[i])

    def parseAgent(self, agent: str):
        self.empty = False
        if agent.find("/") == -1:
            self.agentKey = agent
            return
        parts = agent.split("/")
        if len(parts) != 2:
            print("OEFURI::parseAgent got invalid arguments: {} ({})".format(agent, len(parts)))
            self.empty = True
            return
        self.agentKey = parts[0]
        self.agentAlias = parts[1]

    class Builder:
        def __init__(self):
            self._uri = OEFURI()
            self._uri.empty = False

        def protocol(self, protocol: str):
            self._uri.protocol = protocol
            return self

        def coreAddress(self, core_address: str, core_port: int):
            self._uri.coreURI = "{}:{}".format(core_address, core_port)
            return self

        def coreKey(self, core_key: str):
            self._uri.coreKey = core_key
            return self

        def agentKey(self, agent_key: str):
            self._uri.agentKey = agent_key
            return self

        def agentAlias(self, agent_alias: str):
            self._uri.agentAlias = agent_alias
            return self

        def addNamespace(self, nspace: str):
            self._uri.namespaces.append(nspace)
            return self

        def build(self):
            print("Built URI: ", self._uri.toString())
            return self._uri


class Context:
    def __init__(self):
        self.targetURI = OEFURI()
        self.sourceURI = OEFURI()
        self.serviceId = ""
        self.agentAlias = ""

    def update(self, target: str, source: str):
        self.targetURI.parse(target)
        self.sourceURI.parse(source)
        self.serviceId = self.targetURI.agentAlias
        self.agentAlias = self.targetURI.agentAlias

    def swap(self):
        tmp = self.targetURI
        self.targetURI = self.sourceURI
        self.sourceURI = tmp

    def forAgent(self, target: str, source: str, same_alias: bool = False):
        self.targetURI.parseAgent(target)
        self.sourceURI.parseAgent(source)
        if same_alias:
            self.sourceURI.agentAlias = self.targetURI.agentAlias
        self.serviceId = self.targetURI.agentAlias

    def print(self):
        print("Context: target={}, source={}".format(self.targetURI, self.sourceURI))
