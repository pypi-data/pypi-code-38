

class CommandLineInputMixin:
    max_password_length = 32

    def _parse_from_generated(self, args, f=None):
        params = {}
        f = f or (lambda x: x)
        for arg in args:
            if str.count(arg, '=') != 1:
                self.fail(f"Invalid format : {arg}")
            key, length = str.split(arg, '=')
            params[key] = f(length)

        return params

    def _validate_length(self, length):
        if not length.isdigit():
            self.fail("Argument after = must be numeric.")
        length = int(length)
        if length > self.max_password_length:
            self.fail(f"Maximum length is {self.max_password_length}")
        return length
