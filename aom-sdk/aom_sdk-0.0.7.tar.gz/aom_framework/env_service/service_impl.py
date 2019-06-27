from aom_framework.services_pb2_grpc import EnvironmentServicer as Servicer
from aom_framework.services_pb2_grpc import (
    add_EnvironmentServicer_to_server as add_servicer_to_server)

from aom_framework.common import ENABLE_REFLECTION_VAR_NAME

from aom_framework.protocols_pb2 import (
    EnvStartRequest, EnvStartReply, EnvUpdateRequest, EnvUpdateReply)

import aom_framework.services_pb2 as _service_pbs

from distutils.util import strtobool
import os
import grpc
from grpc_reflection.v1alpha import reflection
from concurrent.futures import ThreadPoolExecutor


# Implementation of the AoM environment service.
class EnvService(Servicer):
    def __init__(self, factory, env_start_pb, user_input_pb, agent_input_pb):
        # We will be managing a pool of environments, keyed by their session id.
        self._envs = {}
        self._factory = factory
        self._env_start_pb = env_start_pb
        self._user_input_pb = user_input_pb
        self._agent_input_pb = agent_input_pb

        print("Environment service started")

    # The orchestrator is requesting a new environment
    def Start(self, request, context):
        # The orchestrator will force a session id on to us, but for testing,
        # it's convenient to be able to create a unique one on demand.

        sess_id = ''
        if request.session_id != '':
            sess_id = request.session_id
        else:
            sess_id = str(uuid.uuid1())
            print("Start: Requestor did not provide a session id, creating one...")

        # Sanity check: We should only ever create a session once.
        if sess_id in self._envs:
            raise Exception("session already exists")

        print(f"spinning up new environment: {sess_id}")

        cfg = self._env_start_pb()
        cfg.ParseFromString(request.user_request.content)

        # Instantiate the fresh environment
        env = self._factory(cfg)
        self._envs[sess_id] = env

        # Send the initial state of the environment back to the client (orchestrator, normally.)
        reply = EnvStartReply(session_id=sess_id)

        reply.initial_sim_state.tick_id = 0
        reply.initial_sim_state.content = env.game_state.SerializeToString()

        return reply

    # The orchestrator is ready for the environemnt to move forward in time.
    def Update(self, request, context):
        sess_id = request.session_id

        if sess_id not in self._envs:
            raise Exception("session does not exists")

        # Retrieve the environment that matches this session
        env = self._envs[sess_id]

        # Extract the Puzzle-teach specific data from the AoM-generic structures
        user_data = self._user_input_pb()
        agent_data = self._agent_input_pb()

        # This is fine for puzzleteach since there is ALWAYS one user and one agent connected.
        user_data.ParseFromString(request.user_data[0].content)
        agent_data.ParseFromString(request.agent_data[0].content)

        # Advance time
        delta = env.update(user_data, agent_data)

        # Send the delta back to the orchestrator.
        reply = EnvUpdateReply()
        reply.delta.content = delta.SerializeToString()

        return reply


def launch_server(port, factory, env_start_pb, user_input_pb, agent_input_pb):
    server = grpc.server(ThreadPoolExecutor(max_workers=10))

    add_servicer_to_server(EnvService(factory, env_start_pb, user_input_pb, agent_input_pb), server)

    if strtobool(os.getenv(ENABLE_REFLECTION_VAR_NAME, 'false')):
        SERVICE_NAMES = (
            _service_pbs.DESCRIPTOR.services_by_name['Environment'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port(f'[::]:{port}')
    server.start()

    print(f"Environment Service listening on port {port}")

    return server
