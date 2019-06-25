from aihub.__aihub__ import AIHub as ai

AIHub = ai


def client(self_token=None):
    return ai().client(self_token)
