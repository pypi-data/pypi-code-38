import os

# Defaults
DEFAULT_AGE = 1
DEFAULT_TYPE = "news"
DEFAULT_NUMBER = 1
DEFAULT_PROXY = os.environ.get("http_proxy") or os.environ.get("https_proxy")


def argValidator(args):
    # This function validates the arguments passed by the user
    # Returns a tuple (newsType, age, number, proxy, config)
    # The type checking is automatically done by the argParse module
    newsType = None
    age = None
    number = None
    proxy = None
    if args.type != None and args.type in ["news", "latest", "past"]:
        newsType = args.type

    elif args.type != None and args.type not in ["news", "latest", "past"]:
        print(
            "WARNING ! Invalid type argument. Using default = {}".format(DEFAULT_TYPE)
        )
        newsType = DEFAULT_TYPE
    else:
        newsType = DEFAULT_TYPE

    if args.age != None and args.age > 1:
        age = args.age
    elif args.age != None and args.age < 1:
        print("WARNING ! Invalid age argument. Using default = {}".format(DEFAULT_AGE))
        age = DEFAULT_AGE
    else:
        age = DEFAULT_AGE

    if args.number != None and args.number > 1 and args.number < 10:
        number = args.number
    elif args.number != None and args.number < 1 or args.number > 10:
        print(
            "WARNING ! Invalid number argument. Using default = {}".format(
                DEFAULT_NUMBER
            )
        )
        number = DEFAULT_NUMBER
    else:
        number = DEFAULT_NUMBER

    if args.proxy != None:
        print("USING PROXY {}".format(args.proxy))
        proxy = args.proxy
    else:
        proxy = DEFAULT_PROXY
    return (newsType, age, number, proxy)

