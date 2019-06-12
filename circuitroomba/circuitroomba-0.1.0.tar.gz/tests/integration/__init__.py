"""
Integration test only work/make sense to run if you hook your board up to a Roomba
Open Interface device and run the suite to validate the bot and board communicate.

These can't be ran in CI due to using the board Circuit Python module which will
raise NotImplementedError: Board not supported.

For unit test this is handled via mocking and patching the necessary packages.
"""
