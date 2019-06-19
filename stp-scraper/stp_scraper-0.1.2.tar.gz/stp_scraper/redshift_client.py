import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


class RedshiftClient:
    def __init__(
        self, database: str, user: str, password: str, host: str, port: str
    ):
        self.connection_string = (
            f'redshift+psycopg2://{user}:{password}@{host}:{port}/{database}'
        )
        self.engine = sa.create_engine(self.connection_string)
        self.sessionmaker = sessionmaker(bind=self.engine)
        self.s = self.sessionmaker()

    def execute(self, query: str) -> list:
        return self.s.execute(query)

    def commit(self) -> None:
        return self.s.commit()
