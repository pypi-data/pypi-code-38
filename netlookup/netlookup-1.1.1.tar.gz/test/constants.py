
VALID_SUBNET_VALUES = (
    '0.0.0.0/0',
    '10.0.0.0/8',
    '2c0f:fb50:5000::',
    '2c0f:fb50:4000::/36',
)

# Invalid values for subnets
INVALID_SUBNET_VALUES = (
    '0.0.0.0/33',
    '10.0.0.256/32',
    '2c0f:fb50:4000::/',
    '2c0f:fb50:4000::/129',
)

# How many times we may try splitting
MAX_SPLITS = 8
