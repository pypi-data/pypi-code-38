class MssqlConnector():
    def get_odbc_connection_url(self, db_host: str, db_port: str, db_database: str, db_user: str, db_password: str) -> str:
        """
        Get odbc connection url.
        
        Parameters
        ----------
        db_host : str
            db host
        db_port : str
            db port
        db_database : str
            database name
        db_user : str
            db user
        db_password : str
            db password
        
        Returns
        ----------
        connection_url : str
            DB connection url
        """
        pass

    def get_session(self, connection_url: str) -> sessionmaker:
        """
        Get session with connection url. Please use other public 
        method of this class to generate connection url.
        
        Parameters
        ----------
        connection_url : str
            connection url
        
        Returns
        ----------
        Session : sqlalchemy.orm.sessionmaker
            db session maker
        """
        pass

