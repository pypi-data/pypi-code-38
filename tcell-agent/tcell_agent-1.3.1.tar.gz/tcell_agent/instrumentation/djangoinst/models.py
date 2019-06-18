from django.utils.datastructures import MultiValueDict

from tcell_agent.instrumentation.headers_cleaner import headers_from_environ


class TCellDjangoRequest(object):
    def __init__(self, request):
        self.request = request

        try:
            self.content_length = int(
                request.META.get("CONTENT_LENGTH", 0)
            )
        except Exception:
            self.content_length = 0
        self.content_type = parse_content_type(request)

        self.normalized_headers = headers_from_environ(request.META)

        self.filenames_dict = normalize_filenames(request.FILES)

    def is_multipart(self):
        self.content_type.startswith("multipart/form-data")

    def is_json(self):
        self.content_type.startswith('application/json')


def normalize_filenames(files_multi_dict):
    if not files_multi_dict:
        return None
    results = MultiValueDict()
    for param_name in files_multi_dict.keys():
        files_obj_list = files_multi_dict.getlist(param_name)
        for file_obj in files_obj_list:
            filename = file_obj.name
            results[param_name] = filename
    return results


def parse_content_type(request):
    return request.META.get("CONTENT_TYPE", "").lower()
