BLACKLISTED_FILES = {
    ".DS_Store"
}

WHITELISTED_FILEEXTS = {
    "ipynb",
}

DEFAULT_SUPPORTED_OPTIONS = {
    "frameworks": {
        "values": [
            "caffe",
            "mxnet",
            "pytorch",
            "tensorflow",
        ],
    },
    "machine_types": {
        "values": [
            "CPU",
            "K80",
            "V100",
        ],
        "default": "CPU",
    },
}
