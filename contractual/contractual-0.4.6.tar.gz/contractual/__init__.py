from collections import defaultdict
from unittest.mock import MagicMock

from .__version__ import __version__


class ContractStore:
    def __init__(self):
        self.providers = defaultdict(dict)

    def __call__(self, _contract, call, response, _provider=None, _given=None):
        provider = self.providers[_provider]
        key = f"{_contract}_{_given}_{call}"
        if key in provider:
            assert (
                provider[key] == response
            ), "Tried to create two different responses for one call"
        else:
            provider[key] = response

    def check(self, _contract, call, response, _provider=None, _given=None) -> bool:
        provider = self.providers.get(_provider, {})
        key = f"{_contract}_{_given}_{call}"
        return key in provider and provider[key] == response


class ContractMock(MagicMock):
    # store[contract_name][given][call] = ret_val
    contract_store = ContractStore()

    def __init__(self, _contract, _given=None, _provider=None, **kwargs):
        super().__init__(**kwargs)
        self.__contract_args = {
            "_provider": _provider,
            "_contract": _contract,
            "_given": _given,
        }

    def _mock_call(_mock_self, *args, **kwargs):
        self = _mock_self
        ret_val = super()._mock_call(*args, **kwargs)
        call = self.call_args.__repr__()
        ContractMock.contract_store(call=call, response=ret_val, **self.__contract_args)
        return ret_val

    @classmethod
    def reset_store(cls):
        cls.contract_store = ContractStore()

    def _get_child_mock(self, **kw):
        """Create the child mocks for attributes and return value.
        By default child mocks will be the same type as the parent.
        Subclasses of Mock may want to override this to customize the way
        child mocks are made.

        For non-callable mocks the callable variant will be used (rather than
        any custom subclass)."""
        kw = dict(kw, **self.__contract_args)
        attribute = "." + kw["name"] if "name" in kw else "()"
        kw["_contract"] = self.__contract_args["_contract"] + attribute
        return super()._get_child_mock(**kw)
