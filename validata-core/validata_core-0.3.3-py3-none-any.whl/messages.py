import re
from datetime import datetime

FRENCH_DATE_RE = re.compile(r'^[0-3]\d/[0-1]\d/[12]\d{3}$')
DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')


def improve_messages(errors, schema):
    """Translates and improve error messages"""

    def error_message_default_func(error, schema):
        """Sets a new better error message"""
        error['title'] = error['code']
        error['content'] = error.get('message', 'pas d\'information complémentaire')
        return error

    improved_errors = []

    for error in errors:

        improve_func = ERROR_MESSAGE_FUNC.get(error['code'], error_message_default_func)
        improved_errors.append(improve_func(error, schema))

    return improved_errors


def u_err(err, title, content):
    """Update error"""
    err['title'] = title
    err['content'] = content
    return err


def et_join(values):
    """french enum
    >>> et_join([])
    ''
    >>> et_join(['a'])
    'a'
    >>> et_join(['a','b'])
    'a et b'
    >>> et_join(['a','b','c'])
    'a, b et c'
    >>> et_join(['a','b','c','d','e'])
    'a, b, c, d et e'
    """
    if values is None or len(values) == 0:
        return ''
    if len(values) == 1:
        return values[0]
    return ' et '.join([', '.join(values[:-1]), values[-1]])

# Core goodtables checks
# -> error message title is stored in 'title' attribute
# -> error message content is stored in 'content' attribute
# This is adapted to pophover display


def blank_header(err, schema):
    """blank-header error"""
    return u_err(err, 'Colonne sans en-tête', 'Toutes les colonnes doivent contenir une en-tête')


def blank_row(err, schema):
    """blank-row error"""
    return u_err(err, 'Ligne vide', 'Les lignes vides doivent être retirées de la table')


def duplicate_header(err, schema):
    """duplicate-header error"""
    return u_err(err, 'En-tête répétée', 'Les colonnes doivent avoir des en-têtes uniques')


def duplicate_row(err, schema):
    """duplicate-row error"""
    msg_prefix = 'La ligne est identique '
    row_number_str = err['message-data']['row_numbers']
    if not ',' in row_number_str:
        msg = msg_prefix + "à la ligne {}.".format(row_number_str)
    else:
        msg = msg_prefix + "aux lignes {}.".format(et_join(row_number_str.split(', ')))
    msg += "\n\nVous pouvez la supprimer."
    return u_err(err, 'Ligne dupliquée', msg)


def extra_value(err, schema):
    """extra-value error"""
    return u_err(err, 'Valeur surnuméraire', "Le nombre de cellules de cette ligne excède" +
                 " le nombre de colonnes défini dans le schéma")


def enumerable_constraint(err, schema):
    """enumerable-constraint"""
    constraint_values = eval(err['message-data']['constraint'])
    ok_values = ['"{}"'.format(val) for val in constraint_values]
    if len(ok_values) == 1:
        return u_err(err, 'Valeur incorrecte', 'L\'unique valeur autorisée pour cette colonne est: {}'.format(ok_values[0]))
    else:
        markdown_str = '\n'.join(['- {}'.format(val.strip('"')) for val in ok_values])
        return u_err(err, 'Valeur incorrecte', 'Les seules valeurs autorisées pour cette colonne sont :\n {}'.format(markdown_str))


def maximum_constraint(err, schema):
    """maximum-constraint"""
    max_value = err['message-data']['constraint']
    return u_err(err, 'Valeur trop grande', 'La valeur attendue doit être inférieure à {}'.format(max_value))


def maximum_length_constraint(err, schema):
    """maximum-length-constraint"""
    max_value = err['message-data']['constraint']
    text_value_len = len(err['message-data']['value'])
    return u_err(err, 'Valeur trop longue', 'La valeur texte attendue ne doit pas comporter plus de {} caractère(s) (au lieu de {} actuellement)'.format(max_value, text_value_len))


def minimum_constraint(err, schema):
    """minimum-constraint"""
    min_value = err['message-data']['constraint']
    return u_err(err, 'Valeur trop petite', 'La valeur attendue doit être au moins égale à {}'.format(min_value))


def minimum_length_constraint(err, schema):
    """minimum-length-constraint"""
    min_value = err['message-data']['constraint']
    text_value_len = len(err['message-data']['value'])
    return u_err(err, 'Valeur trop courte', 'Le texte attendu doit comporter au moins {} caractère(s) (au lieu de {} actuellement)'.format(min_value, text_value_len))


def pattern_constraint(err, schema):
    """pattern-constraint"""
    column_number = err['column-number']
    field = schema['fields'][column_number - 1]
    info_list = []
    if 'description' in field:
        info_list.append('{}\n'.format(field['description']))
    if 'example' in field:
        info_list.append("## Exemple(s) valide(s)\n{}\n".format(field['example']))
    msg = '\n'.join(info_list) if info_list else '*Aucune description ni exemple à afficher.*'
    return u_err(err, 'Format incorrect', msg)


def required_constraint(err, schema):
    """required-constraint error"""
    return u_err(err, 'Cellule vide', 'Une valeur doit être renseignée.')


def type_or_format_error(err, schema):
    """type-or-format-error"""
    err_type = err['message-data']['field_type']
    err_value = err['message-data']['value']

    # Date
    if err_type == 'date':
        # Checks if date is dd/mm/yyyy
        dm = FRENCH_DATE_RE.match(err_value)
        if dm:
            iso_date = datetime.strptime(err_value, '%d/%m/%Y').strftime('%Y-%m-%d')
            return u_err(err, 'Format de date incorrect', "La forme attendue est \"{}\"".format(iso_date))

        # Checks if date is yyyy-mm-ddThh:MM:ss
        # print('DATE TIME ? [{}]'.format(err_value))
        dm = DATETIME_RE.match(err_value)
        if dm:
            iso_date = err_value[:err_value.find('T')]
            return u_err(err, 'Format de date incorrect', "La forme attendue est \"{}\"".format(iso_date))

        # Default date err msg
        return u_err(err, 'Format de date incorrect', 'La date doit être écrite sous la forme `aaaa-mm-jj`.')

    # Year
    elif err_type == 'year':
        return u_err(err, 'Format d\'année incorrect', 'L\'année doit être composée de 4 chiffres')

    # Number
    elif err_type == 'number':
        if ',' in err_value:
            en_number = err_value.replace(',', '.')
            return u_err(err, 'Format de nombre incorrect', "Utilisez le point comme séparateur décimal («&#160;{}&#160;»).".format(en_number))
        return u_err(err, 'Format de nombre incorrect', 'La valeur ne doit comporter que des chiffres et le point comme séparateur décimal.')

    # Number
    elif err_type == 'integer':
        return u_err(err, 'Format entier incorrect', 'La valeur doit être un nombre entier.')

    # String
    elif err_type == 'string':
        return u_err(err, 'Format de chaîne incorrect', 'La valeur doit être une chaîne de caractères.')

    # Boolean
    elif err_type == 'boolean':
        column_number = err['column-number'] - 1
        field = schema['fields'][column_number]
        true_values = field.get('trueValues', ['true'])
        false_values = field.get('falseValues', ['false'])
        true_values_str = et_join(list(map(lambda v: '`{}`'.format(v), true_values)))
        false_values_str = et_join(list(map(lambda v: '`{}`'.format(v), false_values)))
        return u_err(err, "Valeur booléenne incorrecte",
                     "Les valeurs acceptées sont {} (vrai) et {} (faux)".format(true_values_str, false_values_str))

    # Default msg
    return u_err(err, 'Type ou format incorrect', 'La valeur de la cellule n\'est pas de type {}'.format(err_type))


def unique_constraint(err, schema):
    """unique-constraint"""
    msg_prefix = 'Cette valeur est déjà présente '
    row_numbers = err['message-data']['row_numbers']
    if not ',' in row_numbers:
        msg = msg_prefix + "à la ligne {}.".format(row_numbers)
    else:
        msg = msg_prefix + "aux lignes {}.".format(et_join(row_numbers))
    msg += " Or une contrainte d'unicité est définie pour cette colonne."
    msg += "Veuillez corriger les doublons de retirez la contrainte d'unicité du schéma."
    return u_err(err, 'Valeur déjà utilisée', msg)


# Validata custom checks


def french_siret_value(err, schema):
    """french-siret-value error"""
    return u_err(err, 'Numéro SIRET non valide',
                 'Le numéro de SIRET indiqué n\'est pas valide selon la définition de l\'[INSEE](https://www.insee.fr/fr/metadonnees/definition/c1841)')


def compare_columns_value(err, schema):
    """compare-columns-value"""
    return u_err(err, 'Comparaison de colonne', err['message'])


def cohesive_columns_value(err, schema):
    """cohesive-columns-value"""
    return u_err(err, 'Cohérence entre colonnes', err['message'])


def year_interval_value(err, schema):
    """year-interval-value"""
    return u_err(err, 'Année ou période', err['message'])

# Validata pre-checks
#
# -> Error message is stored in 'message' key


def invalid_column_delimiter(err, schema):
    """invalid-column-delimiter"""
    md = err['message-data']
    msg_tpl = 'Le fichier CSV utilise le délimiteur de colonne « {} » au lieu du délimiteur attendu  « {} ».'
    err['message'] = msg_tpl.format(md.get('detected'), md.get(
        'expected')) + "  \nPour vous permettre de continuer la validation, un remplacement automatique a été réalisé."
    return u_err(err, 'Délimiteur de colonne invalide', err['message'])


def missing_headers(err, schema):
    """missing-headers"""
    cols = err['message-data']['headers']
    if len(cols) == 1:
        err['message'] = "La colonne \"{}\" n'a pas été trouvée dans le fichier".format(cols[0])
    else:
        col_list = ''.join(['- {}\n'.format(col) for col in cols])
        fields_nb = len(schema.get('fields', []))
        addon_info = '\nUtilisez-vous le bon schéma ?' if len(cols) == fields_nb else ''
        err['message'] = "Les colonnes suivantes étaient attendues mais n'ont pas été trouvées dans le fichier :\n{}{}".format(
            col_list, addon_info)
    return u_err(err, 'Colonne(s) manquante(s)', err['message'])


def extra_headers(err, schema):
    """extra-headers"""
    cols = err['message-data']['headers']
    if len(cols) == 1:
        err['message'] = "La colonne \"{}\" est inconnue dans le schéma".format(cols[0])
    else:
        col_list = ''.join(['- {}\n'.format(col) for col in cols])
        # addon_info = 'Utilisez-vous le bon schéma ?' if len(cols) == len(headers) else ''
        err['message'] = "Les colonnes suivantes ont été trouvées dans le fichier mais n'étaient pas attendues :\n{}".format(
            col_list)
    return u_err(err, 'Colonne(s) surnuméraire(s)', err['message'])


def wrong_headers_order(err, schema):
    """wrong-headers-order"""
    return u_err(err, 'Ordre des colonnes',
                 'Les colonnes du tableau ne sont pas dans l\'ordre défini par le schéma')


ERROR_MESSAGE_FUNC = {

    # Core checks
    'blank-header': blank_header,
    'blank-row': blank_row,
    'duplicate-header': duplicate_header,
    'duplicate-row': duplicate_row,
    'enumerable-constraint': enumerable_constraint,
    'extra-value': extra_value,
    'maximum-constraint': maximum_constraint,
    'maximum-length-constraint': maximum_length_constraint,
    'minimum-constraint': minimum_constraint,
    'minimum-length-constraint': minimum_length_constraint,

    # These 3 errors are skipped
    # - non-matching-header
    # - extra-header
    # - missing-header
    #  and replaced by 3 aggregated errors:
    # - missing-headers
    # - extra-headers
    # - wrong-headers-order

    # missing-value
    'pattern-constraint': pattern_constraint,
    'required-constraint': required_constraint,
    'type-or-format-error': type_or_format_error,
    'unique-constraint': unique_constraint,

    # Validata pre-checks
    'extra-headers': extra_headers,
    'invalid-column-delimiter': invalid_column_delimiter,
    'missing-headers': missing_headers,
    'wrong-headers-order': wrong_headers_order,

    # Validata custom checks
    'french-siret-value': french_siret_value,
    'compare-columns-value': compare_columns_value,
    'cohesive-columns-value': cohesive_columns_value,
    'year-interval-value': year_interval_value,
}

ERROR_MESSAGE_DEFAULT_TITLE = {

    # Core checks
    'blank-header': 'colonne sans en-tête',
    'blank-row': 'ligne vide',
    'duplicate-header': 'en-tête répété',
    'duplicate-row': 'ligne dupliquée',
    'enumerable-constraint': 'valeur incorrecte',
    'maximum-constraint': 'valeur maximale non respectée',
    'maximum-length-constraint': 'longueur maximale non respectée',
    'minimum-constraint': 'valeur minimale non respectée',
    'minimum-length-constraint': 'longueur minimale non respectée',

    # These 3 errors are skipped
    # - non-matching-header
    # - extra-header
    # - missing-header
    #  and replaced by 3 aggregated errors:
    # - missing-headers
    # - extra-headers
    # - wrong-headers-order

    # missing-value
    'pattern-constraint': 'erreur de format',
    'required-constraint': 'valeur requise',
    'type-or-format-error': 'format incorrect',
    'unique-constraint': 'doublons',

    # Validata pre-checks
    'extra-headers': 'en-tête surnuméraire',
    'invalid-column-delimiter': 'délimiteur de colonne incorrect',
    'missing-headers': 'en-tête manquant',
    'wrong-headers-order': 'en-têtes non ordonnés',

    # Validata custom checks
    'french-siret-value': 'n° siret invalide',
    'compare-columns-value': 'comparaison de colonne invalide',
    'cohesive-columns-value': 'cohérence entre colonnes',
    'year-interval-value': 'année ou période',
}
