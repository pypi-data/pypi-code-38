class GenericWorklog:
    def __init__(self, projectKey=None, issueKey=None, date=None, durationInSeconds=None, description=None):
        self.projectKey = projectKey
        self.issueKey = issueKey
        self.durationInSeconds = durationInSeconds
        self.description = description
        self.date = date

    def __format__(self, format):
        if format == 'human':
            value = "{}\n{}\n{}\n{}\n{}".format(
                self.projectKey,
                self.issueKey,
                self.date,
                self.durationInSeconds,
                self.description,
            )

            return value

        return "{} {} {} {} {}".format(
            self.projectKey,
            self.issueKey,
            self.date,
            self.durationInSeconds,
            self.description,
        )
