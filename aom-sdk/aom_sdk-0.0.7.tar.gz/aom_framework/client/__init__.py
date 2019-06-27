import aom_framework.protocols_pb2 as aom_pbs
import aom_framework.services_pb2_grpc as aom_services

import grpc


class Trial:
    def __init__(self, conn, trial, state):
        self.connection = conn
        self.state = state
        self.trial = trial

    def Action(self, user_data):
        update = self.connection.stub.Action(aom_pbs.TrialActionRequest(
            session_id=self.trial.session_id, content=user_data.SerializeToString()))
        delta = self.connection.delta_type()
        delta.ParseFromString(update.delta.content)
        return delta


class Connection:
    def __init__(self, endpoint, state_type, delta_type):
        channel = grpc.insecure_channel(endpoint)
        self.stub = aom_services.TrialStub(channel)
        self.state_type = state_type
        self.delta_type = delta_type

    def Start(self, init_cfg):
        trial = self.stub.Start(aom_pbs.TrialStartRequest(content=init_cfg.SerializeToString()))
        game_state = self.state_type()
        game_state.ParseFromString(trial.initial_sim_state.content)
        return Trial(self, trial, game_state)
