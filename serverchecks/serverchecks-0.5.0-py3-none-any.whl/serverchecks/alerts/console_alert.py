from serverchecks.alerts import AbstractAlert


class ConsoleAlert(AbstractAlert):
    """
    A basic console alert class that will simply display the test result on the console
    """
    name = 'Console'

    def __init__(self, **kwargs) -> None:
        pass

    async def alert(self, message: str) -> None:
        print(message)

    def __str__(self):
        return f'<{self.name}>'


alert_class = ConsoleAlert
