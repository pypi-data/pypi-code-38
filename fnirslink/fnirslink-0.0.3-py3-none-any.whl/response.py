class Response:
    @staticmethod
    def get_data(success, data, message, error_code):
        return_data = dict()
        return_data['success'] = success
        if data is not None :
            return_data['data'] = data
        if error_code is not None :
            return_data['errorCode'] = error_code
        if message is not None :
            return_data['message'] = message
        return return_data

    @staticmethod
    def success():
        return Response.get_data(True , None , None , None)

    @staticmethod
    def success_data(data):
        return Response.get_data(True , data , None , None)

    @staticmethod
    def fail(error_code , message):
        return Response.get_data(False , None , message , error_code)