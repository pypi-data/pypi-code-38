# Admins:  complete control
# Modelers: Can update catalog schema
# Curator: read and write any data
# Writer: Read and write data created by user
# Reader: Can read any data.

# Group configuration for testing

groups = {
    'curator': "https://auth.globus.org/86cd6ee0-16f6-11e9-b9af-0edc9bdd56a6",
    "writer":  "https://auth.globus.org/646933ac-16f6-11e9-b9af-0edc9bdd56a6",
    "reader":  "https://auth.globus.org/4966c7fe-16f6-11e9-8bb8-0ee7d80087ee",
    "isrd":    'https://auth.globus.org/3938e0d0-ed35-11e5-8641-22000ab4b42b',
    "admin": 'https://auth.globus.org/3938e0d0-ed35-11e5-8641-22000ab4b42b',
    'test':    'https://auth.globus.org/5569e3ba-16c4-11e9-95d6-0ee7d80087ee'
}
