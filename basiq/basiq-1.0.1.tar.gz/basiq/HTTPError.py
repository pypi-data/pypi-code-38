class HTTPError(Exception):
    def __init__(self, response):
        self.correlationId = response["correlationId"]
        self.data = response["data"]
        messages = []
        for message in self.data:
            messages.append(message["detail"])
        
        self.msg = ", ".join(messages)

    def get_message(self):
        return self.msg

    def __str__(self):
        return "HTTPError: %s" % self.msg