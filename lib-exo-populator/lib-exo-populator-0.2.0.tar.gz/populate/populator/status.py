class PopulateStatus:
    status = False

    def set_initialized(self):
        self.status = False

    def set_populated(self):
        self.status = True

    def get_status(self):
        return self.status
