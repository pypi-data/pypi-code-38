special_chars = {
  "0_index": "?i",
  "1_index": "?j",
  "original_name": "?o",
  "extension": "?e"
}

if __name__ == "__main__":
    print("Special Characters:")
    for key, value in chars.items():
        print("  " + key + ":", value)
