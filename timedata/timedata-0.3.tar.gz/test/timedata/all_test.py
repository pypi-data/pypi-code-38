import import_all


class ImportAllTest(import_all.ImportAllTest):
    CATCH_EXCEPTIONS = True

    EXCLUDE = 'timedata.instruments.laser.**'
