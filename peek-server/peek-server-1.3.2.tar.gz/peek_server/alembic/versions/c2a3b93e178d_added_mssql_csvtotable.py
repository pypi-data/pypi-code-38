"""Added MSSQL csvtotable

Revision ID: c2a3b93e178d
Revises: 05cf60a0fd22
Create Date: 2017-07-17 10:48:07.127510

"""

# revision identifiers, used by Alembic.
from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.dialects.postgresql.base import PGDialect

revision = 'c2a3b93e178d'
down_revision = '05cf60a0fd22'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2

def isMssqlDialect():
    return isinstance(op.get_bind().engine.dialect, MSDialect)


def isPostGreSQLDialect():
    return isinstance(op.get_bind().engine.dialect, PGDialect)


def upgrade():
    msSqlForVarchar = '''
        CREATE FUNCTION [dbo].[peekCsvVarcharToTable](@input AS Varchar(max) )
        RETURNS
              @Result TABLE(Value varchar(100))
        AS
        BEGIN
              DECLARE @str VARCHAR(20)
              DECLARE @ind Int
              IF(@input is not null)
              BEGIN
                    SET @ind = CharIndex(',',@input)
                    WHILE @ind > 0
                    BEGIN
                          SET @str = SUBSTRING(@input,1,@ind-1)
                          SET @input = SUBSTRING(@input,@ind+1,LEN(@input)-@ind)
                          INSERT INTO @Result values (@str)
                          SET @ind = CharIndex(',',@input)
                    END
                    SET @str = @input
                    INSERT INTO @Result values (@str)
              END
              RETURN
        END
    '''

    msSqlForInt = '''
        CREATE FUNCTION [dbo].[peekCsvIntToTable](@input AS Varchar(max) )
        RETURNS
              @Result TABLE(Value bigint)
        AS
        BEGIN
              DECLARE @str VARCHAR(20)
              DECLARE @ind Int
              IF(@input is not null)
              BEGIN
                    SET @ind = CharIndex(',',@input)
                    WHILE @ind > 0
                    BEGIN
                          SET @str = SUBSTRING(@input,1,@ind-1)
                          SET @input = SUBSTRING(@input,@ind+1,LEN(@input)-@ind)
                          INSERT INTO @Result values (@str)
                          SET @ind = CharIndex(',',@input)
                    END
                    SET @str = @input
                    INSERT INTO @Result values (@str)
              END
              RETURN
        END
    '''

    if isMssqlDialect():
        op.execute(msSqlForVarchar)
        op.execute(msSqlForInt)


def downgrade():
    raise NotImplementedError()
