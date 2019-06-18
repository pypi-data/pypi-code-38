
BASE_URL = 'https://www.thisamericanlife.org'

API_PATH = dict(
    staff='/about/staff',
    episode='/{episode_number}/{episode_title}',
    transcript='/{episode_number}/transcript',
    recommendations=dict(
        new_to_tal='/recommended/new-to-this-american-life',
        staff='/recommended/staff-recommendations'
    )
)


def get_full_url_template(path_name):
    return BASE_URL + API_PATH[path_name]
