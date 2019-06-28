if __name__ == 'userspy.sqlite':

    def create_table(c, name, cols):
        cols_string = ''  # (
        i = 0
        for e in cols:
            if i != 0:
                cols_string += ','
                cols_string += ' '

            cols_string += e[0] + ' ' + e[1].upper()

            i += 1
        # cols_string += ')'

        c.execute(f'CREATE TABLE IF NOT EXISTS {name}({cols_string})')

    def Remove(c, name, username):
        c.execute(f"DELETE FROM {name} WHERE username={username}")

    def insert(c, conn, name, data):
        data_string = ''
        i = 0
        for e in data:
            if i != 0:
                data_string += ','
                data_string += ' '

            data_string += f"'{e}'"

            i += 1
        c.execute(f'INSERT INTO {name} VALUES({data_string})')

    def read(c, name):
        c.execute(f'SELECT * FROM {name}')
        return c.fetchall()
