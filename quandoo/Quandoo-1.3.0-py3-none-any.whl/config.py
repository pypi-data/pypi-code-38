version = "v1"

# TEST = True
TEST = False

base_url = "https://api.quandoo.com"
base_url_test = "https://test-api.quandoo.com"

url = base_url_test * int(TEST) + base_url * int(not TEST)
