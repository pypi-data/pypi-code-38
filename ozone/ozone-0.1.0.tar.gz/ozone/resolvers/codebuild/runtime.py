import boto3
import re


CODEBUILD_PLATFORMS = ['UBUNTU']

def cleanup_version(version_str):
    """
    Function that replaces the parts of the string as decribed in pairs in the dict
    Allows to run a sub(x, y, str) of another sub for each key of hte dict
    """
    dict = {
        'aws/codebuild/': '',
        '.': '',
        ':': '',
        '-': '',
        '_': ''
    }
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    return regex.sub(lambda word: dict[word.string[word.start():word.end()]], version_str)


def generate_runtime_mapping_and_parameters(languages):
    client = boto3.client('codebuild')
    try:
        mappings = {}
        params_languages = []
        params_versions = []
        platform_mappings = {}
        platforms = client.list_curated_environment_images()['platforms']
        for platform in platforms:
            if platform['platform'] in CODEBUILD_PLATFORMS:
                platform_key = platform['platform'].lower()
                platform_mappings[platform_key] = {}
                for language in platform['languages']:
                    if language['language'].lower() in languages:
                        language_name = language['language']
                        language_key = cleanup_version(language['language'].lower())
                        params_languages.append(language_key)
                        platform_mappings[platform_key][language_key] = {}
                        for image in language['images']:
                            language_version = cleanup_version(image['name'])
                            params_versions.append(language_version)
                            platform_mappings[platform_key][language_key][language_version] = language_version
                            platform_mappings[platform_key][language_key][language_version] = image['versions'][-1]
        mappings = {}
        for platform in CODEBUILD_PLATFORMS:
            key = platform.lower()
            for j in platform_mappings[key]:
                mappings[j] = platform_mappings[key][j]
        return (True, mappings, params_languages, params_versions)
    except Exception as error:
        return None

if __name__ == '__main__':
    import json
    print(json.dumps(
        generate_runtime_mapping_and_parameters(['python', 'node_js', 'docker']),
        indent=2
    ))

