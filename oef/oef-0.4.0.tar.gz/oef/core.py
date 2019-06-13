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


"""

oef.core
~~~~~~~~

The core module that contains the main abstraction of the SDK.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from oef import agent_pb2 as agent_pb2
from oef.messages import CFP_TYPES, PROPOSE_TYPES, OEFErrorOperation
from oef.query import Query, SearchResultItem
from oef.schema import Description
from oef import utils

logger = logging.getLogger(__name__)


class OEFCoreInterface(ABC):
    """Methods to interact with an OEF node."""

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the OEF Node

        :return: True if the connection has been established, False otherwise.
        """

    @abstractmethod
    def register_agent(self, msg_id: int, agent_description: Description) -> None:
        """
        Adds a description of an agent to the OEF so that it can be understood/ queried by
        other agents in the OEF.

        :param msg_id: the identifier of the message.
        :param agent_description: description of the agent to add
        :return: ``None``
        """

    @abstractmethod
    def register_service(self, msg_id: int, service_description: Description, service_id: str = "") -> None:
        """
        Adds a description of the respective service so that it can be understood/queried by
        other agents in the OEF.

        :param msg_id: the identifier of the message.
        :param service_description: description of the services to add
        :param service_id: unique ID for the service, needs to be used if the agent wants to register more then one service
        :return: ``None``
        """

    @abstractmethod
    def search_agents(self, msg_id: int, query: Query) -> None:
        """
        Search for other agents it is interested in communicating with. This can
        be useful when an agent wishes to directly proposition the provision of a service that it
        thinks another agent may wish to be able to offer it. All matching agents are returned
        (potentially including ourselves).

        :param msg_id: the identifier of the message.
        :param query: specifications of the constraints on the agents that are matched
        :return: ``None``.
        """

    @abstractmethod
    def search_services(self, msg_id: int, query: Query) -> None:
        """
        Search for a particular service. This allows constrained search of all
        services that have been registered with the OEF. All matching services will be returned
        (potentially including services offered by ourselves).

        :param msg_id: the identifier of the message.
        :param query: the constraint on the matching services
        :return: ``None``.
        """

    @abstractmethod
    def search_services_wide(self, msg_id: int, query: Query) -> None:
        """
        Search for a particular service widely. This allows constrained search of all
        services that have been registered with the OEF Search. All matching services will be returned
        (potentially including services offered by ourselves).

        :param msg_id: the identifier of the message.
        :param query: the constraint on the matching services
        :return: ``None``.
        """

    @abstractmethod
    def unregister_agent(self, msg_id: int) -> None:
        """
        Remove the description of an agent from the OEF. This agent will no longer be queryable
        by other agents in the OEF. A conversation handler must be provided that allows the agent
        to receive and manage conversations from other agents wishing to communicate with it.

        :param msg_id: the identifier of the message.

        :return: ``None``
        """

    @abstractmethod
    def unregister_service(self, msg_id: int, service_description: Description, service_id: str = "") -> None:
        """
        Add a description of the respective service so that it can be understood/queried by
        other agents in the OEF.

        :param msg_id: the identifier of the message.
        :param service_description: description of the services to add
        :param service_id: service id to unregister, default is empty
        :return: ``None``
        """

    @abstractmethod
    def send_message(self, msg_id: int, dialogue_id: int, destination: str, msg: bytes) -> None:
        """
        Send a simple message.

        :param msg_id: the identifier of the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param msg: the message (in bytes).
        :param context: Context object containing target and source URIs
        :return: ``None``
        """

    @abstractmethod
    def send_cfp(self, msg_id: int, dialogue_id: int, destination: str, target: int, query: CFP_TYPES, context: utils.Context) -> None:
        """
        Send a Call-For-Proposals.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param target: the identifier of the message to whom this message is answering.
        :param query: the query associated with the Call For Proposals.
        :param context: Context object containing target and source URIs
        :return: ``None``
        """

    @abstractmethod
    def send_propose(self, msg_id: int, dialogue_id: int, destination: str, target: int,
                     proposals: PROPOSE_TYPES, context: utils.Context) -> None:
        """
        Send a Propose.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param target: the identifier of the message to whom this message is answering.
        :param proposals: either a list of :class:`~oef.schema.Description` or ``bytes``.
        :param context: Context object containing target and source URIs
        :return: ``None``
        """

    @abstractmethod
    def send_accept(self, msg_id: int, dialogue_id: int, destination: str, target: int, context: utils.Context) -> None:
        """
        Send an Accept.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param target: the identifier of the message to whom this message is answering.
        :param context: Context object containing target and source URIs
        :return: ``None``
        """

    @abstractmethod
    def send_decline(self, msg_id: int, dialogue_id: int, destination: str, target: int, context: utils.Context) -> None:
        """
        Send a Decline.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param target: the identifier of the message to whom this message is answering.
        :param context: Context object containing target and source URIs
        :return: ``None``
        """

    @abstractmethod
    async def stop(self):
        """Stop the proxy."""


class DialogueInterface(ABC):
    """
    The methods of this interface are the callbacks that are called from the OEFProxy
    when a certain message has to be delivered to an agent.
    The names of the method match the pattern 'on' followed by the name of the message.
    """

    @abstractmethod
    def on_message(self, msg_id: int,
                   dialogue_id: int,
                   origin: str,
                   content: bytes) -> None:
        """
        Handler for simple messages.

        :param msg_id: the message identifier for the dialogue.
        :param origin: the identifier of the agent who sent the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param content: the content of the message (in bytes).
        :return: ``None``
        """

    @abstractmethod
    def on_cfp(self, msg_id: int,
               dialogue_id: int,
               origin: str,
               target: int,
               query: CFP_TYPES) -> None:
        """
        Handler for CFP messages.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param origin: the identifier of the agent who sent the message.
        :param target: the identifier of the message to whom this message is answering.
        :param query: the query associated with the Call For Proposals.
        :return: ``None``
        """

    @abstractmethod
    def on_propose(self, msg_id: int,
                   dialogue_id: int,
                   origin: str,
                   target: int,
                   proposals: PROPOSE_TYPES) -> None:
        """
        Handler for Propose messages.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param origin: the identifier of the agent who sent the message.
        :param target: the identifier of the message to whom this message is answering.
        :param proposals: the proposal associated with the message.
        :return: ``None``
        """

    @abstractmethod
    def on_accept(self, msg_id: int,
                  dialogue_id: int,
                  origin: str,
                  target: int) -> None:
        """
        Handler for Accept messages.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param origin: the identifier of the agent who sent the message.
        :param target: the identifier of the message to whom this message is answering.
        :return: ``None``
        """

    @abstractmethod
    def on_decline(self, msg_id: int,
                   dialogue_id: int,
                   origin: str,
                   target: int) -> None:
        """
        Handler for Decline messages.

        :param msg_id: the message identifier for the dialogue.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param origin: the identifier of the agent who sent the message.
        :param target: the identifier of the message to whom this message is answering.
        :return: ``None``
        """

    async def async_on_message(self, msg_id: int,
                               dialogue_id: int,
                               origin: str,
                               content: bytes) -> None:
        """
        The same of :func:`~oef.core.DialogueInterface.on_message`, but in asynchronous context.
        """
        self.on_message(msg_id, dialogue_id, origin, content)

    async def async_on_cfp(self, msg_id: int,
                           dialogue_id: int,
                           origin: str,
                           target: int,
                           query: CFP_TYPES) -> None:
        """
        The same of :func:`~oef.core.DialogueInterface.on_cfp`, but in asynchronous context.
        """
        self.on_cfp(msg_id, dialogue_id, origin, target, query)

    async def async_on_propose(self, msg_id: int,
                               dialogue_id: int,
                               origin: str,
                               target: int,
                               proposals: PROPOSE_TYPES) -> None:
        """
        The same of :func:`~oef.core.DialogueInterface.on_propose`, but in asynchronous context.
        """
        self.on_propose(msg_id, dialogue_id, origin, target, proposals)

    async def async_on_accept(self, msg_id: int,
                              dialogue_id: int,
                              origin: str,
                              target: int) -> None:
        """
        The same of :func:`~oef.core.DialogueInterface.on_accept`, but in asynchronous context.
        """
        self.on_accept(msg_id, dialogue_id, origin, target)

    async def async_on_decline(self, msg_id: int,
                               dialogue_id: int,
                               origin: str,
                               target: int) -> None:
        """
        The same of :func:`~oef.core.DialogueInterface.on_decline`, but in asynchronous context.
        """
        self.on_decline(msg_id, dialogue_id, origin, target)


class ConnectionInterface(ABC):
    """Methods to handle error and search result messages from the OEF Node."""

    @abstractmethod
    def on_oef_error(self, answer_id: int, operation: OEFErrorOperation) -> None:
        """
        Handler for error messages from the OEF node.

        :param answer_id: the id of the message that generated the error.
        :param operation: the operation that caused the error.

        :return: ``None``
        """

    @abstractmethod
    def on_dialogue_error(self, answer_id: int, dialogue_id: int, origin: str) -> None:
        """
        Handler for error messages concerning dialogues between agents.

        :param answer_id: the id of the message that generated the error.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param origin: the identifier of the agent that generated the error.

        :return: ``None``
        """

    @abstractmethod
    def on_search_result(self, search_id: int, agents: List[str]) -> None:
        """
        Handler for Search Result messages.

        :param search_id: the identifier of the search to whom the result is answering.
        :param agents: the list of identifiers of the agents compliant with the search constraints.
        :return: ``None``
        """

    @abstractmethod
    def on_search_result_wide(self, search_id: int, agents: List[SearchResultItem]) -> None:
        """
        Handler for Search Result Wide messages.
        :param search_id: the identifier of the search to whom the result is answering.
        :param agents: the list of identifiers of the agents compliant with the search constraints.
        :return: ``None``
        """

    async def async_on_oef_error(self, answer_id: int, operation: OEFErrorOperation) -> None:
        """
        The same of :func:`~oef.core.ConnectionInterface.on_oef_error`, but in asynchronous context.
        """
        self.on_oef_error(answer_id, operation)

    async def async_on_dialogue_error(self, answer_id: int, dialogue_id: int, origin: str) -> None:
        """
        The same of :func:`~oef.core.ConnectionInterface.on_dialogue_error`, but in asynchronous context.
        """
        self.on_dialogue_error(answer_id, dialogue_id, origin)

    async def async_on_search_result(self, search_id: int, agents: List[str]) -> None:
        """
        The same of :func:`~oef.core.ConnectionInterface.on_search_result`, but in asynchronous context.
        """
        self.on_search_result(search_id, agents)


class AgentInterface(DialogueInterface, ConnectionInterface, ABC):
    """
    Interface to be implemented by agents.
    It contains methods from:

    * :class:`~oef.core.DialogueInterface`, that contains handlers for the incoming messages from other agents
    * :class:`~oef.core.ConnectionInterface`, that contains handlers for error and search result messages from the OEF.
    """


class OEFProxy(OEFCoreInterface, ABC):
    """Abstract definition of an OEF Proxy."""

    def __init__(self, public_key: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        self._public_key = public_key
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._active_loop = True
        self._context_store = {}

    @property
    def public_key(self) -> str:
        """The public key used by the proxy to communicate with the OEF Node."""
        return self._public_key

    @abstractmethod
    async def _receive(self) -> bytes:
        """
        Receive a message from the OEF Node

        :return: the bytes received from the communication channel.
        """

    def getContext(self, message_id: int, dialogue_id: int, origin: str):
        return self._context_store.get("{}:{}:{}".format(message_id, dialogue_id, origin), utils.Context())

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the proxy is currently connected to the OEF Node.

        :return: ``True`` if the proxy is connected, ``False`` otherwise.
        """

    async def loop(self, agent: AgentInterface) -> None:  # noqa: C901
        """
        Event loop to wait for messages and to dispatch the arrived messages to the proper handler.

        :param agent: the implementation of the message handlers specified in AgentInterface.
        :return: ``None``
        """
        while self._active_loop:
            try:
                data = await self._receive()
            except asyncio.CancelledError:
                logger.debug("Proxy {}: loop cancelled".format(self.public_key))
                break
            msg = agent_pb2.Server.AgentMessage()
            msg.ParseFromString(data)
            case = msg.WhichOneof("payload")
            logger.debug("loop {0}".format(case))

            if case == "agents":
                await agent.async_on_search_result(msg.answer_id, msg.agents.agents)
            elif case == "agents_wide":
                result_items = []
                for item in msg.agents_wide.result:
                    core_key  = str(item.key,'ascii')
                    core_addr = item.ip
                    distance = item.distance
                    core_port = item.port
                    for agt in item.agents:
                        agent_key = str(agt.key, 'ascii')
                        result_items.append(SearchResultItem(agent_key, core_key, core_addr, core_port, distance))
                agent.on_search_result_wide(msg.answer_id, result_items)
            elif case == "oef_error":
                await agent.async_on_oef_error(msg.answer_id, OEFErrorOperation(msg.oef_error.operation))
            elif case == "dialogue_error":
                await agent.async_on_dialogue_error(msg.answer_id,
                                                    msg.dialogue_error.dialogue_id,
                                                    msg.dialogue_error.origin)
            elif case == "content":
                entry_key = "{}:{}:{}".format(msg.answer_id, msg.content.dialogue_id, msg.content.origin)
                self._context_store[entry_key] = utils.Context()
                self._context_store[entry_key].update(msg.target_uri, msg.source_uri)
                content_case = msg.content.WhichOneof("payload")
                logger.debug("msg content {0}".format(content_case))
                try:
                    if content_case == "content":
                        await agent.async_on_message(msg.answer_id, msg.content.dialogue_id, msg.content.origin, msg.content.content)
                    elif content_case == "fipa":
                        fipa = msg.content.fipa
                        fipa_case = fipa.WhichOneof("msg")
                        if fipa_case == "cfp":
                            cfp_case = fipa.cfp.WhichOneof("payload")
                            if cfp_case == "nothing":
                                query = None
                            elif cfp_case == "content":
                                query = fipa.cfp.content
                            elif cfp_case == "query":
                                query = Query.from_pb(fipa.cfp.query)
                            else:
                                raise Exception("Query type not valid.")
                            await agent.async_on_cfp(msg.answer_id, msg.content.dialogue_id, msg.content.origin,
                                                     fipa.target, query)
                        elif fipa_case == "propose":
                            propose_case = fipa.propose.WhichOneof("payload")
                            if propose_case == "content":
                                proposals = fipa.propose.content
                            else:
                                proposals = [Description.from_pb(propose) for propose in fipa.propose.proposals.objects]
                            await agent.async_on_propose(msg.answer_id, msg.content.dialogue_id, msg.content.origin,
                                                         fipa.target, proposals)
                        elif fipa_case == "accept":
                            await agent.async_on_accept(msg.answer_id, msg.content.dialogue_id, msg.content.origin,
                                                        fipa.target)
                        elif fipa_case == "decline":
                            await agent.async_on_decline(msg.answer_id, msg.content.dialogue_id, msg.content.origin,
                                                         fipa.target)
                        else:
                            logger.warning("Not implemented yet: fipa {0}".format(fipa_case))
                finally:
                    self._context_store.pop(entry_key)

            else:
                print("UNKNOWN CASE: ", case)
                exit(76)
