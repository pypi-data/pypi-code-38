from aom_framework.services_pb2_grpc import AgentServicer as Servicer
from aom_framework.services_pb2_grpc import add_AgentServicer_to_server as add_servicer_to_server

from aom_framework.common import ENABLE_REFLECTION_VAR_NAME

from aom_framework.protocols_pb2 import (
    AgentStartRequest, AgentStartReply, AgentDecideRequest,
    AgentDecideReply, AgentRewardRequest, AgentRewardReply)


import aom_framework.services_pb2 as _service_pbs

from distutils.util import strtobool
import os
import grpc
from grpc_reflection.v1alpha import reflection
from concurrent.futures import ThreadPoolExecutor


# Implementation of the AoM environment service.
class AgentService(Servicer):
    def __init__(self, factory, env_state_pb):
        print("Agent Service started")
        # We will be managing a pool of agents, keyed by their session id.
        self._agents = {}
        self._factory = factory
        self._env_state_pb = env_state_pb

    # The orchestrator is requesting a new environment
    def Start(self, request, context):
        # The orchestrator will force a session id on to us, but for testing,
        # it's convenient to be able to create a unique one on demand.
        sess_id = request.session_id

        if not sess_id:
            raise Exception("No session ID provided")

        # Sanity check: We should only ever create a session once.
        if sess_id in self._agents:
            raise Exception("session already exists")

        # Instantiate the fresh agent
        agent = self._factory()
        self._agents[sess_id] = (agent, self._env_state_pb())

        # Send the initial state of the environment back to the client (orchestrator, normally.)
        reply = AgentStartReply()

        return reply

    # The orchestrator is ready for the environemnt to move forward in time.
    def Decide(self, request, context):
        sess_id = request.session_id

        if sess_id not in self._agents:
            raise Exception("session does not exists.")

        # Retrieve the environment that matches this session
        agent, state = self._agents[sess_id]

        if request.HasField('env_state'):
            state.ParseFromString(request.env_state.content)
        elif request.HasField('env_delta'):
            pass
#      delta = env_pb.GameStateDelta()
#      delta.ParseFromString(request.env_delta.env_specific_data)
#      pt_utils.advance_inplace(state, delta)
        else:
            raise Exception("no env data.")

        decision = agent.decide_from_state(state)

        # Send the delta back to the orchestrator.
        reply = AgentDecideReply()
        reply.decision.content = decision.SerializeToString()

        return reply

    def Reward(self, request, context):
        sess_id = request.session_id

        if sess_id not in self._agents:
            raise Exception("session does not exists.")

        # Retrieve the environment that matches this session
        agent, state = self._agents[sess_id]

        agent.reward()

        reply = AgentRewardReply()

        return reply


def launch_server(port, factory, env_state_pb):
    server = grpc.server(ThreadPoolExecutor(max_workers=10))

    add_servicer_to_server(AgentService(factory, env_state_pb), server)

    if strtobool(os.getenv(ENABLE_REFLECTION_VAR_NAME, 'false')):
        SERVICE_NAMES = (
            _service_pbs.DESCRIPTOR.services_by_name['Agent'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port(f'[::]:{port}')
    server.start()

    print(f"Agent Service listening on port {port}")

    return server
