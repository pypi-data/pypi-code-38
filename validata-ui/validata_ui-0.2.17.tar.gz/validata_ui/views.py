"""
    Routes
"""
import copy
import io
import itertools
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from urllib.parse import urlencode, urljoin

import requests
import tableschema
import tabulator
from backports.datetime_fromisoformat import MonkeyPatch
from commonmark import commonmark
from flask import abort, make_response, redirect, render_template, request, url_for
from validata_core import messages

from opendataschema import GitSchemaReference, by_commit_date

from . import app, config, schema_catalog_registry, tableschema_from_url
from .ui_util import flash_error, flash_warning
from .validata_util import UploadedFileValidataResource, URLValidataResource, ValidataResource

MonkeyPatch.patch_fromisoformat()

log = logging.getLogger(__name__)


def get_schema_catalog(section_name):
    """Return a schema catalog associated to a section_name"""
    return schema_catalog_registry.build_schema_catalog(section_name)


class SchemaInstance:
    """Handy class to handle schema information"""

    def __init__(self, parameter_dict):
        """Initializes schema instance from requests dict and tableschema catalog (for name ref)"""
        self.section_name = None
        self.section_title = None
        self.name = None
        self.url = None
        self.ref = None
        self.reference = None
        self.doc_url = None
        self.branches = None
        self.tags = None

        # From schema_url
        if parameter_dict.get("schema_url"):
            self.url = parameter_dict["schema_url"]
            self.section_title = "Autre schéma"

        # from schema_name (and schema_ref)
        elif parameter_dict.get('schema_name'):
            self.schema_and_section_name = parameter_dict['schema_name']
            self.ref = parameter_dict.get('schema_ref')

            # Check schema name
            chunks = self.schema_and_section_name.split('.')
            if len(chunks) != 2:
                abort(400, "Paramètre 'schema_name' invalide")

            self.section_name, self.name = chunks
            self.section_title = self.find_section_title(self.section_name)

            # Look for schema catalog first
            table_schema_catalog = get_schema_catalog(self.section_name)
            if table_schema_catalog is None:
                abort(400, "Section '{}' non trouvée dans la configuration".format(self.section_name))

            schema_reference = table_schema_catalog.reference_by_name.get(self.name)
            if schema_reference is None:
                abort(400, "Schéma '{}' non trouvé dans le catalogue de la section '{}'".format(self.name, self.section_name))

            if isinstance(schema_reference, GitSchemaReference):
                self.tags = sorted(schema_reference.iter_tags(), key=by_commit_date, reverse=True)
                if self.ref is None:
                    schema_ref = self.tags[0] if self.tags else schema_reference.get_default_branch()
                    abort(redirect(compute_validation_form_url({
                        'schema_name': self.schema_and_section_name,
                        'schema_ref': schema_ref.name
                    })))
                tag_names = [tag.name for tag in self.tags]
                self.branches = [branch for branch in schema_reference.iter_branches()
                                 if branch.name not in tag_names]
                self.doc_url = schema_reference.get_doc_url(ref=self.ref) or \
                    schema_reference.get_project_url(ref=self.ref)

            self.url = schema_reference.get_schema_url(ref=self.ref)

        else:
            abort(400, "L'un des paramètres est nécessaire : 'schema_name', 'schema_url'")

        try:
            self.schema = tableschema_from_url(self.url)
        except json.JSONDecodeError as e:
            log.exception(e)
            flash_error("Format de schéma non reconnu")
            abort(redirect(url_for('home')))
        except Exception as e:
            log.exception(e)
            flash_error("Erreur lors de l'obtention du schéma")
            abort(redirect(url_for('home')))

    def request_parameters(self):
        if self.name:
            return {
                'schema_name': self.schema_and_section_name,
                'schema_ref': '' if self.ref is None else self.ref
            }
        return {
            'schema_url': self.url
        }

    def find_section_title(self, section_name):
        if config.HOMEPAGE_CONFIG:
            for section in config.HOMEPAGE_CONFIG['sections']:
                if section["name"] == section_name:
                    return section.get("title")
        return None


def extract_source_data(source: ValidataResource, preview_rows_nb=5):
    """ Computes table preview """

    def stringify(val):
        """ Transform value into string """
        return '' if val is None else str(val)

    header = None
    rows = []
    nb_rows = 0

    tabulator_source, tabulator_options = source.build_tabulator_stream_args()
    with tabulator.Stream(tabulator_source, **tabulator_options) as stream:
        for row in stream:
            if header is None:
                header = ['' if v is None else v for v in row]
            else:
                rows.append(list(map(stringify, row)))
                nb_rows += 1
    preview_rows_nb = min(preview_rows_nb, nb_rows)
    return {'header': header,
            'rows_nb': nb_rows,
            'data_rows': rows,
            'preview_rows_nb': preview_rows_nb,
            'preview_rows': rows[:preview_rows_nb]}


def improve_errors(errors):
    """Add context to errors, converts markdown content to HTML"""

    def improve_err(err):
        """Adds context info based on row-nb presence and converts content to HTML"""

        # Context
        update_keys = {
            'context': 'body' if 'row-number' in err and not err['row-number'] is None else 'table',
        }

        # markdown to HTML (with default values for 'title' and 'content')

        # Set default title if no title
        if not 'title' in err:
            update_keys['title'] = '[{}]'.format(err['code'])

        # Convert message to markdown only if no content
        # => for pre-checks errors
        if 'message' in err and not 'content' in err:
            update_keys['message'] = commonmark(err['message'])

        # Else, default message
        elif not 'message' in err or err['message'] is None:
            update_keys['message'] = '[{}]'.format(err['code'])

        # Message content
        md_content = '*content soon available*' if not 'content' in err else err['content']
        update_keys['content'] = commonmark(md_content)

        return {**err, **update_keys}

    return list(map(improve_err, errors))


def create_validata_ui_report(validata_core_report, schema_dict):
    """ Creates an error report easier to handle and display in templates:
        - only one table
        - errors are contextualized
        - error-counts is ok
        - errors are grouped by lines
        - errors are separated into "structure" and "body"
        - error messages are improved
    """
    report = copy.deepcopy(validata_core_report)

    # One table is enough
    del report['table-count']
    report['table'] = report['tables'][0]
    del report['tables']
    del report['table']['error-count']
    del report['table']['time']
    del report['table']['valid']
    del report['valid']
    # use _ instead of - to ease information picking in jinja2 template
    report['table']['row_count'] = report['table']['row-count']

    # Handy col_count info
    headers = report['table'].get('headers', [])
    report['table']['col_count'] = len(headers)

    # Computes column info
    fields_dict = {f['name']: (f.get('title', 'titre non défini'), f.get('description', ''))
                   for f in schema_dict.get('fields', [])}
    report['table']['headers_title'] = [fields_dict[h][0] if h in fields_dict else 'colonne inconnue' for h in headers]
    report['table']['headers_description'] = [fields_dict[h][1]
                                              if h in fields_dict else 'Cette colonne n\'est pas définie dans le schema' for h in headers]

    # Provide better (french) messages
    errors = improve_errors(report['table']['errors'])
    del report['table']['errors']

    # Count errors
    report['error_count'] = len(errors)
    del report['error-count']

    # Then group them in 2 groups : structure and body
    report['table']['errors'] = {'structure': [], 'body': []}
    for err in errors:
        if err['tag'] == 'structure':
            report['table']['errors']['structure'].append(err)
        else:
            report['table']['errors']['body'].append(err)

    # Checks if there are structure errors different to invalid-column-delimiter
    structure_errors = report['table']['errors']['structure']
    report['table']['do_display_body_errors'] = len(structure_errors) == 0 or \
        all(err['code'] == 'invalid-column-delimiter' for err in structure_errors)

    # Checks if a column comparison is needed
    header_errors = ('missing-headers', 'extra-headers', 'wrong-headers-order')
    structure_errors = [{**err, 'in_column_comp': err['code'] in header_errors} for err in structure_errors]
    report['table']['errors']['structure'] = structure_errors
    column_comparison_needed = any(err['in_column_comp'] == True for err in structure_errors)
    column_comparison_table = []
    if column_comparison_needed:
        column_comparison_table = []
        field_names = [f['name'] for f in schema_dict.get('fields', [])]
        has_case_errors = False
        for t in itertools.zip_longest(headers, field_names, fillvalue=''):
            status = 'ok' if t[0] == t[1] else 'ko'
            if not has_case_errors and status == 'ko' and t[0].lower() == t[1].lower():
                has_case_errors = True
            column_comparison_table.append((*t, status))
        info = {}
        info['table'] = column_comparison_table
        info['has_missing'] = len(headers) < len(field_names)
        info['has_case_errors'] = has_case_errors
        report['table']['column_comparison_info'] = info
    report['table']['column_comparison_needed'] = column_comparison_needed

    # Group body errors by row id
    rows = []
    current_row_id = 0
    for err in report['table']['errors']['body']:
        if not 'row-number' in err:
            print('ERR', err)
        row_id = err['row-number']
        del err['row-number']
        del err['context']
        if row_id != current_row_id:
            current_row_id = row_id
            rows.append({'row_id': current_row_id, 'errors': {}})

        column_id = err.get('column-number')
        if column_id is not None:
            del err['column-number']
            rows[-1]['errors'][column_id] = err
        else:
            rows[-1]['errors']['row'] = err
    report['table']['errors']['body_by_rows'] = rows

    # Sort by error names in statistics
    stats = report['table']['error-stats']
    code_title_map = messages.ERROR_MESSAGE_DEFAULT_TITLE
    for key in ('structure-errors', 'value-errors'):
        # convert dict into tuples with french title instead of error code
        # and sorts by title
        stats[key]['count-by-code'] = sorted(((code_title_map.get(k, k), v)
                                              for k, v in stats[key]['count-by-code'].items()), key=itemgetter(0))

    return report


def compute_badge_message_and_color(badge):
    """Computes message and color from badge information"""
    structure = badge['structure']
    body = badge.get('body')

    # Bad structure, stop here
    if structure == 'KO':
        return ('structure invalide', 'red')

    # No body error
    if body == 'OK':
        return ('structure invalide', 'orange') if structure == 'WARN' else ('valide', 'green')

    # else compute quality ratio percent
    p = (1 - badge['error-ratio']) * 100.0
    msg = 'cellules valides : {:.1f}%'.format(p)
    return (msg, 'red') if body == 'KO' else (msg, 'orange')


def get_badge_url_and_message(badge):
    """Gets badge url from badge information"""

    msg, color = compute_badge_message_and_color(badge)
    badge_url = "{}?{}".format(
        urljoin(config.SHIELDS_IO_BASE_URL, '/static/v1.svg'),
        urlencode({"label": "Validata", "message": msg, "color":  color}),
    )
    return (badge_url, msg)


def validate(schema_instance: SchemaInstance, source: ValidataResource):
    """ Validate source and display report """

    # Useful to receive response as JSON
    headers = {"Accept": "application/json"}

    try:
        if source.type == 'url':
            params = {
                "schema": schema_instance.url,
                "url": source.url,
            }
            response = requests.get(config.API_VALIDATE_ENDPOINT, params=params, headers=headers)
        else:
            files = {'file': (source.filename, source.build_reader())}
            data = {"schema": schema_instance.url}
            response = requests.post(config.API_VALIDATE_ENDPOINT, data=data, files=files, headers=headers)
    except requests.ConnectionError as err:
        logging.exception(err)
        flash_error("Erreur technique lors de la validation")
        return redirect(url_for('home'))

    if not response.ok:
        flash_error("Erreur technique lors de la validation")
        return redirect(compute_validation_form_url(schema_instance.request_parameters()))

    json_response = response.json()
    validata_core_report = json_response['report']
    badge_info = json_response.get('badge')

    # Computes badge from report and badge configuration
    badge_url, badge_msg = None, None
    display_badge = badge_info and config.SHIELDS_IO_BASE_URL
    if display_badge:
        badge_url, badge_msg = get_badge_url_and_message(badge_info)

    source_errors = [
        err
        for err in validata_core_report['tables'][0]['errors']
        if err['code'] in {'source-error', 'unknown-csv-dialect'}
    ]
    if source_errors:
        err = source_errors[0]
        msg = "l'encodage du fichier est invalide. Veuillez le corriger" if 'charmap' in err[
            'message'] else err['message']
        flash_error('Erreur de source : {}'.format(msg))
        return redirect(url_for('custom_validator'))

    source_data = extract_source_data(source)

    # handle report date
    report_datetime = datetime.fromisoformat(validata_core_report['date']).astimezone()

    # Enhance validata_core_report
    validata_report = create_validata_ui_report(validata_core_report, schema_instance.schema.descriptor)

    # Display report to the user
    validator_form_url = compute_validation_form_url(schema_instance.request_parameters())
    schema_info = compute_schema_info(schema_instance.schema, schema_instance.url)
    pdf_report_url = "{}?{}".format(url_for('pdf_report'),
                                    urlencode({
                                        **schema_instance.request_parameters(),
                                        "url": source.url,
                                    })) if source.type == 'url' else None

    return render_template('validation_report.html',
                           badge_msg=badge_msg,
                           badge_url=badge_url,
                           breadcrumbs=[
                               {'title': 'Accueil', 'url': url_for('home')},
                               {'title': schema_instance.section_title},
                               {'title': schema_info['title'], 'url': validator_form_url},
                               {'title': 'Rapport de validation'},
                           ],
                           display_badge=display_badge,
                           doc_url=schema_instance.doc_url,
                           pdf_report_url=pdf_report_url,
                           print_mode=request.args.get('print', 'false') == 'true',
                           report_str=json.dumps(validata_report, sort_keys=True, indent=2),
                           report=validata_report,
                           schema_current_version=schema_instance.ref,
                           schema_info=schema_info,
                           section_title=schema_instance.section_title,
                           source_data=source_data,
                           source=source,
                           validation_date=report_datetime.strftime('le %d/%m/%Y à %Hh%M'),
                           )


def bytes_data(f):
    """ Gets bytes data from Werkzeug FileStorage instance """
    iob = io.BytesIO()
    f.save(iob)
    iob.seek(0)
    return iob.getvalue()


# Routes


@app.route('/')
def home():
    """ Home page """

    def iter_sections():
        """Yield sections of the home page, filled with schema metadata."""
        if not config.HOMEPAGE_CONFIG:
            return
        for section in config.HOMEPAGE_CONFIG['sections']:
            home_section = {k: v for k, v in section.items() if k != 'catalog'}
            if "catalog" in section:
                schema_catalog = get_schema_catalog(section['name'])
                if schema_catalog:
                    home_section_catalog = []
                    for schema_reference in schema_catalog.references:
                        # Loads default table schema for each schema reference
                        table_schema = tableschema_from_url(schema_reference.get_schema_url())
                        home_section_catalog.append({
                            "name": schema_reference.name,
                            "title": table_schema.descriptor.get("title") or schema_reference.name,
                        })
                    home_section['catalog'] = home_section_catalog
            if "links" in section:
                home_section["links"] = section["links"]
            yield home_section

    return render_template('home.html', sections=list(iter_sections()))


@app.route('/pdf')
def pdf_report():
    """PDF report generation"""
    err_prefix = 'Erreur de génération du rapport PDF'

    url_param = request.args.get('url')
    if not url_param:
        flash_error(err_prefix + ' : URL non fournie')
        return redirect(url_for('home'))

    schema_instance = SchemaInstance(request.args)

    # Compute pdf url report
    base_url = url_for('custom_validator', _external=True)
    parameter_dict = {
        'input': 'url',
        'print': 'true',
        'url': url_param,
        **schema_instance.request_parameters()
    }
    validation_url = "{}?{}".format(base_url, urlencode(parameter_dict))

    # Create temp file to save validation report
    with tempfile.NamedTemporaryFile(prefix='validata_{}_report_'.format(datetime.now().timestamp()), suffix='.pdf') as tmpfile:
        tmp_pdf_report = Path(tmpfile.name)

    # Use chromium headless to generate PDF from validation report page
    cmd = ['chromium', '--headless', '--no-sandbox',
           '--print-to-pdf={}'.format(str(tmp_pdf_report)), validation_url]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        flash_error(err_prefix)
        log.error("Command %r returned an error: %r", cmd, result.stdout.decode('utf-8'))
        if tmp_pdf_report.exists():
            tmp_pdf_report.unlink()
        return redirect(url_for('home'))

    # Send PDF report
    pdf_filename = 'Rapport de validation {}.pdf'.format(datetime.now().strftime('%d-%m-%Y %Hh%M'))
    response = make_response(tmp_pdf_report.read_bytes())
    response.headers.set('Content-disposition', 'attachment', filename=pdf_filename)
    response.headers.set('Content-type', 'application/pdf')
    response.headers.set('Content-length', tmp_pdf_report.stat().st_size)

    tmp_pdf_report.unlink()

    return response


def extract_schema_metadata(table_schema: tableschema.Schema):
    """Gets author, contibutor, version...metadata from schema header"""
    return {k: v for k, v in table_schema.descriptor.items() if k != 'fields'}


def compute_schema_info(table_schema: tableschema.Schema, schema_url):
    """Factor code for validator form page"""

    # Schema URL + schema metadata info
    schema_info = {
        'path': schema_url,
        # a "path" metadata property can be found in Table Schema, and we'd like it to override the `schema_url`
        # given by the user (in case schema was given by URL)
        **extract_schema_metadata(table_schema)
    }
    return schema_info


def compute_validation_form_url(request_parameters: dict):
    """Computes validation form url with schema URL parameter"""
    url = url_for('custom_validator')
    return "{}?{}".format(url, urlencode(request_parameters))


@app.route('/table-schema', methods=['GET', 'POST'])
def custom_validator():
    """Validator form"""

    if request.method == 'GET':

        # input is a hidden form parameter to know
        # if this is the initial page display or if the validation has been asked for
        input_param = request.args.get('input')

        # url of resource to be validated
        url_param = request.args.get("url")

        schema_instance = SchemaInstance(request.args)

        # First form display
        if input_param is None:
            schema_info = compute_schema_info(schema_instance.schema, schema_instance.url)
            return render_template('validation_form.html',
                                   branches=schema_instance.branches,
                                   breadcrumbs=[
                                       {'url': url_for('home'), 'title': 'Accueil'},
                                       {'title': schema_instance.section_title},
                                       {'title': schema_info['title']},
                                   ],
                                   doc_url=schema_instance.doc_url,
                                   schema_current_version=schema_instance.ref,
                                   schema_info=schema_info,
                                   schema_params=schema_instance.request_parameters(),
                                   section_title=schema_instance.section_title,
                                   tags=schema_instance.tags,
                                   )

        # Process URL
        else:
            if not url_param:
                flash_error("Vous n'avez pas indiqué d'URL à valider")
                return redirect(compute_validation_form_url(schema_instance.request_parameters()))
            return validate(schema_instance, URLValidataResource(url_param))

    elif request.method == 'POST':

        schema_instance = SchemaInstance(request.form)

        input_param = request.form.get('input')
        if input_param is None:
            flash_error("Vous n'avez pas indiqué de fichier à valider")
            return redirect(compute_validation_form_url(schema_instance.request_parameters()))

        # File validation
        if input_param == 'file':
            f = request.files.get('file')
            if f is None:
                flash_warning("Vous n'avez pas indiqué de fichier à valider")
                return redirect(compute_validation_form_url(schema_instance.request_parameters()))

            return validate(schema_instance, UploadedFileValidataResource(f.filename, bytes_data(f)))

        return 'Combinaison de paramètres non supportée', 400

    else:
        return "Method not allowed", 405
