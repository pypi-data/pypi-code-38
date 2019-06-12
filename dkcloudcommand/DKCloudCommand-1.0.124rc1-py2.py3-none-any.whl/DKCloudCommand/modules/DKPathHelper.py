import os


class DKPathHelper:
    FORCE_WINDOWS = False

    WIN = 'windows'
    UNIX = 'unix'

    def __init__(self):
        pass

    @staticmethod
    def normalize(path, mode):
        if not DKPathHelper.is_windows_os():
            return path
        ret = path
        if path is not None:
            if mode == DKPathHelper.WIN:
                ret = path.replace("/", "\\")
            else:
                ret = path.replace("\\", "/")
        return ret

    @staticmethod
    def normalize_list(the_list, mode):
        if not DKPathHelper.is_windows_os():
            return the_list
        ret_list = list()
        if the_list is None:
            return the_list
        for item in the_list:
            ret_list.append(DKPathHelper.normalize(item, mode))
        return ret_list

    @staticmethod
    def normalize_dict_keys(the_dict, mode, ignore=None):
        if not DKPathHelper.is_windows_os():
            return the_dict
        if not ignore:
            ignore = []
        if the_dict is None:
            return the_dict
        ret_dict = dict()
        for key, value in the_dict.iteritems():
            if key not in ignore:
                new_key = DKPathHelper.normalize(key, mode)
            else:
                new_key = key
            ret_dict[new_key] = value
        return ret_dict

    @staticmethod
    def normalize_dict_value(the_dict, the_key, mode):
        if not DKPathHelper.is_windows_os():
            return the_dict
        if the_dict is None:
            return the_dict
        if the_key not in the_dict:
            return the_dict

        the_old_value = the_dict[the_key]
        the_new_value = DKPathHelper.normalize(the_old_value, mode)

        the_dict[the_key] = the_new_value
        return the_dict

    @staticmethod
    def normalize_recipe_dict(rdict, mode):
        if not DKPathHelper.is_windows_os():
            return rdict
        if rdict and 'recipes' in rdict:
            for k, v in rdict['recipes'].iteritems():
                if isinstance(v, dict):
                    rdict['recipes'][k] = DKPathHelper.normalize_dict_keys(v, mode)
        return rdict

    @staticmethod
    def normalize_recipe_dict_kmp(rdict, mode):
        if not DKPathHelper.is_windows_os():
            return rdict
        if rdict and 'results' in rdict:
            new_list = list()
            for item in rdict['results']:
                if isinstance(item, dict) and 'file' in item:
                    item['file'] = DKPathHelper.normalize(item['file'], mode)
                new_list.append(item)
            rdict['results'] = new_list
        return rdict

    @staticmethod
    def normalize_merge_kitchens_improved(rdict, mode):
        if not DKPathHelper.is_windows_os():
            return rdict
        if rdict and 'merge-kitchen-result' in rdict and 'merge_info' in rdict['merge-kitchen-result'] and \
                'recipes' in rdict['merge-kitchen-result']['merge_info']:

            if rdict['merge-kitchen-result']['merge_info']['recipes']:
                the_recipes = rdict['merge-kitchen-result']['merge_info']['recipes']
                the_new_recipes = dict()
                for the_recipe_name in the_recipes.keys():
                    the_new_recipe = DKPathHelper.normalize_dict_keys(the_recipes[the_recipe_name], mode)
                    the_new_recipes[the_recipe_name] = the_new_recipe
                rdict['merge-kitchen-result']['merge_info']['recipes'] = the_new_recipes
        return rdict

    @staticmethod
    def normalize_get_compiled_file(file_data, mode):
        if not DKPathHelper.is_windows_os():
            return file_data
        if file_data and 'path' in file_data:
            file_data['path'] = DKPathHelper.normalize(file_data['path'], mode)
        return file_data

    @staticmethod
    def normalize_recipe_validate(the_return_list, mode):
        if not DKPathHelper.is_windows_os():
            return the_return_list
        if the_return_list and isinstance(the_return_list, list):
            for item in the_return_list:
                if isinstance(item, dict) and 'file' in item:
                    item['file'] = DKPathHelper.normalize(item['file'], mode)
        return the_return_list

    @staticmethod
    def is_windows_os():
        if DKPathHelper.FORCE_WINDOWS:
            return True
        ret = False
        if os.name == 'nt':
            ret = True
        return ret

