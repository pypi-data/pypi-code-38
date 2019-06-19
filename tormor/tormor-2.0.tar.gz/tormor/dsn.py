import os

# Dictionary of possible options
PGOPTMAP = {
    "-d": ("dbname", "PGDATABASE", "/dbname"), 
    "-h": ("host", "PGHOST", "@host"), 
    "-p": ("port", "PGPORT", ":port"), 
    "-U": ("user", "PGUSER", "user"),
    "-P": ("password", "PGPASSWORD", ":password")
}

# Create a string of "mapped_filed = value"
def makeDSN(destination):
    template = "postgresql://user:password@host:port/dbname"
    for option, (field, env, placeholder) in PGOPTMAP.items():
        if destination[option]:
            template = template.replace(field, destination[option])
        elif os.getenv(env):
            template = template.replace(field, os.getenv(env))
        else:
            template = template.replace(placeholder, "")
    return template