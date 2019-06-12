# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = cep_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Optional, Any, TypeVar, Type, cast
import json

import requests

T = TypeVar("T")


class viacep:

    @staticmethod
    def consulta_cep(cep):
        response = requests.request("GET", "https://viacep.com.br/ws/{cep}/json/".format(cep=cep))

        if response.status_code == 200:
            return cep_from_dict(json.loads(response.text))
        else:
            return Cep(None, None, None, None, None, None, None, None, None)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Cep:
    cep: Optional[str]
    logradouro: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    localidade: Optional[str]
    uf: Optional[str]
    unidade: Optional[str]
    ibge: Optional[str]
    gia: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'Cep':
        assert isinstance(obj, dict)
        cep = from_union([from_str, from_none], obj.get("cep"))
        logradouro = from_union([from_str, from_none], obj.get("logradouro"))
        complemento = from_union([from_str, from_none], obj.get("complemento"))
        bairro = from_union([from_str, from_none], obj.get("bairro"))
        localidade = from_union([from_str, from_none], obj.get("localidade"))
        uf = from_union([from_str, from_none], obj.get("uf"))
        unidade = from_union([from_str, from_none], obj.get("unidade"))
        ibge = from_union([from_str, from_none], obj.get("ibge"))
        gia = from_union([from_str, from_none], obj.get("gia"))
        return Cep(cep, logradouro, complemento, bairro, localidade, uf, unidade, ibge, gia)

    def to_dict(self) -> dict:
        result: dict = {}
        result["cep"] = from_union([from_str, from_none], self.cep)
        result["logradouro"] = from_union([from_str, from_none], self.logradouro)
        result["complemento"] = from_union([from_str, from_none], self.complemento)
        result["bairro"] = from_union([from_str, from_none], self.bairro)
        result["localidade"] = from_union([from_str, from_none], self.localidade)
        result["uf"] = from_union([from_str, from_none], self.uf)
        result["unidade"] = from_union([from_str, from_none], self.unidade)
        result["ibge"] = from_union([from_str, from_none], self.ibge)
        result["gia"] = from_union([from_str, from_none], self.gia)
        return result


def cep_from_dict(s: Any) -> Cep:
    return Cep.from_dict(s)


def cep_to_dict(x: Cep) -> Any:
    return to_class(Cep, x)
