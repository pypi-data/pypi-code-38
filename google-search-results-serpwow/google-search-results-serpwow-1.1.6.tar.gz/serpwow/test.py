# -*- coding: utf-8 -*-

from google_search_results import GoogleSearchResults
import json

# create the serpwow object, passing in our API key
serpwow = GoogleSearchResults("DC14D724")

extract_keyword_string = '"難民" "世界難民" "子ども" "アフガニスタン難民" "ロヒンギャ難民" -filetype:pdf'

params = {
  "q": extract_keyword_string,
  "filter": "0",
  "start": 0,
  "num": 100,
  "gl": "jp",
  "hl": "ja",
  "google_domain": "google.co.jp",
  "no_cache": "true"
}
# retrieve the search results as JSON
result = serpwow.get_json(params)

# pretty-print the result
first_organic_result_snippet = result["organic_results"][0]["snippet"]
print(first_organic_result_snippet)

#print(json.dumps(result, indent=2, sort_keys=True))