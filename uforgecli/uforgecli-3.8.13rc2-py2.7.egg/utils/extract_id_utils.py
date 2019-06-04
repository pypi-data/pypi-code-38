# Extracts the Id in a string, position parameter is the wished number starting from the end of the string.

def extractId(url, position=None, operation=True):

        final = []
        tuple = url.split("/")
        for item in tuple:
                try:
                        int(item)
                        final.append(item)
                except ValueError:
                        pass
        final = list(reversed(final))
        if position is None:
                position = 0
        if operation:
                return final[position]
        else:
                return final
