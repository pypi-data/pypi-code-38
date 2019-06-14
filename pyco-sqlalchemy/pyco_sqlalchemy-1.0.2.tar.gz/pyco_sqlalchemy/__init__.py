"""
Tips:
- use `charset=UTF8MB4 collate utf8_general_ci`
  (https://stackoverflow.com/questions/766809/whats-the-difference-between-utf8-general-ci-and-utf8-unicode-ci)
- use `ext.TrimColumn instead Columns.Text`

# todo: support simple SQLALchemy-ORM
# todo: support django-ORM
"""

UTF8 = "utf8_general_ci"
UTF8MB4 = "utf8mb4_general_ci"
_UTF8MB4 = "utf8mb4_unicode_ci"
