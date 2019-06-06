class AbstractAlert:
    """
    Abstract alert transport class template. The __init__ method should be non-blocking (just collect
    parameters) while all network comms should be happening in open().
    """

    async def open(self) -> None:
        pass

    async def alert(self, message: str) -> None:
        pass

    async def test(self) -> bool:
        pass

    async def close(self) -> None:
        pass
