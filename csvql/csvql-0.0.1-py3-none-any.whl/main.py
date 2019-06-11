import cmd, sys
from csvrw import CSVRW
from db import DB

class CsvSqlShell(cmd.Cmd):
    intro = 'Welcome to the CSV-SQL shell. Type help or ? to list commands.\n'
    prompt = '(csv-sql) '

    def preloop(self):
        self.result = None
        self.delimiter = ','
        self.header = True
        self.db = DB('../data/sqlite.db')
        super(CsvSqlShell, self).preloop()

    def do_load(self, args):
        'Load an CSV file into the database (args: file_path table_name).'
        file, name = parse(args) # check
        csvrw = CSVRW(file, self.delimiter)
        csv = csvrw.read()
        columns = self.db.columns(csv)
        types = self.db.types(csv, self.header)
        self.db.create_table(name, columns, types)
        self.db.bulk_insert(name, csv, self.header)

    def do_drop(self, arg):
        'Drop a table from the database (arg: table_name).'
        self.db.drop_table(arg)

    def do_query(self, arg):
        """
        Execute an SQL statement on the database (arg: statement).
        Result is stored temporarily, see 'last' and 'unload' commands.
        """
        self.result = self.db.query_db(arg)
        print(f'{len(self.result)} result(s).')

    def do_desc(self, arg):
        'Print the DDL of the table (arg: table_name).'
        self.db.print_sql(arg)

    def do_delim(self, arg):
        "Print or change the current delimiter, default is ',' (arg(optional): new_delimiter)"
        if arg:
            self.delimiter = arg
            print(f"Delimiter changed to '{self.delimiter}'.")
        else:
            print(f"Delimiter is '{self.delimiter}'.")

    def do_header(self, arg):
        "Set header on or off, default is on (arg: 'on'/'off')."
        if arg.lower() == 'on':
            self.header = True
        elif arg.lower() == 'off':
            self.header = False
        else:
            print("Use 'on' or 'off' with this command.")

    def do_last(self, arg):
        "Print the first rows of the last result, default is 20 rows (arg(optional): max_rows)."
        if self.result:
            if arg:
                try:
                    max_rows = int(arg)
                    self.db.print_table(self.result,
                                        header=self.header,
                                        maxr=max_rows)
                except:
                    print("Argument 'max_rows' must be an integer.")
            else:
                self.db.print_table(self.result, header=self.header)
        else:
            print("Use the 'query' command first.")

    def do_tables(self, arg):
        "Print the names of the tables currently loaded."
        self.db.print_tables()

    def do_unload(self, arg):
        "Create CSV file containing last result (arg: file_path)."
        if self.result:
            if arg:
                csvrw = CSVRW(arg, self.delimiter)
                csvrw.write(self.result, self.header)
            else:
                print("Argument 'file_path' missing.")
        else:
            print("Use the 'query' command first.")

def parse(arg):
    'Convert a series of zero or more words to an argument tuple.'
    return tuple(map(str, arg.split()))

if __name__ == '__main__':
    CsvSqlShell().cmdloop()
