import regex
import torch
from torch.distributions.gamma import Gamma
from torch.distributions.categorical import Categorical
import numpy
import math
from typing import List
from kismet.personality.responses import responses as responses_


class Responder:
    def __init__(self, responses=responses_):
        self.categorical = Categorical(torch.ones(len(responses_)))
        self.responses = responses_

    def respond(self, excitement: int):
        response = []
        for i in range(excitement):
            response.append(self.responses[self.categorical.sample()])

        resposnse = " ".join(response)
        return " ".join(response)


responder_ = Responder()


def analyze(string: str, responder: Responder = responder_):
    mentions = len(
        regex.findall(r"[Kk]+\s*[Ii]+\s*[Ss]+\s*[Mm]+\s*[Ee]+\s*[Tt]+", string)
    )
    if mentions:
        attention = numpy.arcsinh(mentions) * numpy.arcsinh(
            math.log(len(string.replace(r"\s", "")))
        )
        excitement = int(torch.ceil(Gamma(1.2, 2 / attention).sample()).tolist())
        return responder.respond(excitement)
    else:
        return None
