from serverchecks import Outcome


class AbstractCheck:

    async def check(self) -> Outcome:
        pass
