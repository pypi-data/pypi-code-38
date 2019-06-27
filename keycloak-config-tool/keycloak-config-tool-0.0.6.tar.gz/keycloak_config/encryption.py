from kmsencryption import decrypt as kmsdecrypt


class EncryptionHelper(object):

    def __init__(self, encryption_prefix, aws_profile):
        """
        Constructor.
        :param encryption_prefix: Encryption prefix used by the KMS toolbox.
        :param aws_profile: AWS profile used for communicating with KMS.
        """
        self.encryption_prefix = encryption_prefix or 'decrypt:'
        self.aws_profile = aws_profile

    def decrypt(self, obj_value):
        if isinstance(obj_value, str):
            return self.decrypt_string(obj_value)
        elif isinstance(obj_value, dict):
            return self.decrypt_dict(obj_value)
        elif isinstance(obj_value, list):
            return self.decrypt_list(obj_value)
        return obj_value

    def decrypt_string(self, string_content):
        if string_content.startswith(self.encryption_prefix):
            print('==== DECRYPTING VALUE "{0}".'.format(string_content))
            return kmsdecrypt(data=string_content, profile=self.aws_profile, prefix=self.encryption_prefix, env=None)
        return string_content

    def decrypt_dict(self, dict_content):
        result = {}
        for key, value in dict_content.items():
            result[key] = self.decrypt(value)
        return result

    def decrypt_list(self, list_content):
        result = []
        for elem in list_content:
            result.append(self.decrypt(elem))
        return result
