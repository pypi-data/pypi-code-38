import imgix

url = 'sherwinski.imgix.net'
path = 'image.jpg'

# with warnings.catch_warnings(record=True) as w:
#     ub = imgix.UrlBuilder(url, sign_with_library_version=False)
#     assert len(w) == 1
#     assert issubclass(w[-1].category, DeprecationWarning)
#     assert "deprecated" in str(w[-1].message)

# ub = imgix.UrlBuilder(url, include_library_param=False)
# ub = imgix.UrlBuilder(url, include_library_param=False)
ub = imgix.UrlBuilder(url)

print("Here's your url: " + ub.create_url(path))
# print(True and None)
