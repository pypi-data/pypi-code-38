"""Google Invoice class file."""

import csv
import datetime
import json
import sys

from io import StringIO

from apiclient import http as apihttp


class Invoice(object):
    """Google Invoice class."""

    def __init__(self, google, bigquery_project=None):
        """Initialize an Invoice instance."""
        self.google = google
        self.storage = self.google.storage().storage
        self.verbose = google.verbose

        # big query project
        # self.bigquery_project = bigquery_project

    def check_content_type(self):
        """Check the content type."""
        if self.type == 'csv':
            contentType = 'text/csv'
        elif self.type == 'json':
            contentType = 'application/json'
        else:
            return

        # check content type and update if necessary
        if self.object['contentType'] != contentType:
            print('   Updating contentType: %s -> %s' % (
                self.object['contentType'],
                contentType,
            ))
            self.object['contentType'] = contentType
            self.update_object_metadata()

    def check_data(self, csv_invoice):
        """Check object media data."""
        csv_data = csv_invoice.data
        json_data = self.data
        if csv_data != json_data:
            self.data = csv_data
            self.update_object_data()

    def check_invoices(self, bucket, project, dataset, table):
        """Check Invoice amounts against BigQuery."""
        # self.bucket = bucket
        # self.project = project
        # self.dataset = dataset
        # self.table = table

        invoices = {}
        for i in self.from_gcs(bucket):
            if i.id not in invoices:
                invoices[i.id] = i
        print('Invoices: %s' % (len(invoices)))

        for invoice_id in sorted(invoices, key=lambda x: invoices[x].get_date()):
            i = invoices[invoice_id]

            # get the invoice month
            invoice_month = ''.join(i.get_date().split('-')[:2])

            # get invoice total from CSV/JSOn data
            invoice_total = i.metadata.get('Invoice amount')
            if not invoice_total:
                invoice_total = i.metadata.get('Invoice subtotal')
            invoice_total = float(invoice_total.replace(',', ''))

            # get bigquery total
            bigquery_total = i.get_bigquery_total(
                project,
                dataset,
                table,
                invoice_month)
            if not bigquery_total:
                print('%s - %s: %s' % (
                    invoice_month,
                    i.id,
                    invoice_total,
                ))
            else:
                diff = bigquery_total - invoice_total
                print('%s - %s: %s [bq diff: %s]' % (
                    invoice_month,
                    i.id,
                    invoice_total,
                    diff
                ))

    def check_metadata(self):
        """Check the metadata."""
        if self.header != self.metadata:
            print('   Updating metatata:')

            keys = set(list(self.header) + list(self.metadata))

            def sort_key(x):
                """Sort for keys."""
                if sys.version_info < (3, 0):
                    # print('Version: %s' % (sys.version_info))
                    if isinstance(x, unicode):
                        return x.encode('utf8', errors='replace')
                    else:
                        return x
                else:
                    return x

            # keys = []
            # # fix keys
            # for key in allkeys:
            #     key = u'%s' % (key)

            # exit
            for key in sorted(keys, key=lambda x: sort_key(x)):
                old = self.metadata.get(key)
                new = self.header.get(key)
                # print(type(old))
                if old != new:
                    print('    * %s: %s -> %s' % (
                        sort_key(key),
                        old,
                        new
                    ))
            self.object['metadata'] = self.header
            # set metadata on the Invoice object
            self.metadata = self.header
            # set metadata  on the GCS object
            self.update_object_metadata()

    def delete_json_invoice(self):
        """Delete a JSON invoice from GCS."""

    def from_gcs(self, bucket):
        """Return invoices from GCS."""
        objects = self.google.storage().get_objects(bucket)
        invoices = []
        for o in objects:
            # skip zero-size objects ("folders")
            if not int(o['size']):
                continue
            invoices.append(self.from_gcs_object(o))
        return invoices

    def from_gcs_object(self, o):
        """Return an Invoice instance from a GCS object."""
        invoice = Invoice(self.google)

        # set bucket and object name
        invoice.bucket = o['bucket']
        invoice.name = o['name']

        # get object metdata
        invoice.metadata = o.get('metadata', {})

        # store object info
        invoice.object = o

        # set the object uri
        invoice.uri = 'gs://%s/%s' % (invoice.bucket, invoice.name)

        # set invoice type (csv/json)
        invoice.type = None
        if '.json' in invoice.name:
            invoice.type = 'json'
        elif '.csv' in invoice.name:
            invoice.type = 'csv'

        # get invoice date
        invoice.date = invoice.get_date()

        # get invoice id
        invoice.id = invoice.get_id()

        return invoice

    def get_bigquery_total(self, project, dataset, table, invoice_month):
        """Return the bigquery results for a given month."""
        table = '%s.%s.%s' % (project, dataset, table)
        query = """SELECT
            invoice.month,
            (SUM(CAST(cost * 1000000 AS int64))
                + SUM(IFNULL((SELECT SUM(CAST(c.amount * 1000000 as int64))
                    FROM UNNEST(credits) c), 0))) / 1000000
                AS total_exact
            FROM `%s`
            WHERE invoice.month = "%s"
            GROUP BY 1""" % (
                table,
                invoice_month
            )
        response = self.google.bigquery().query_job(project, query)
        if not response:
            return
        return float(response[0]['f'][1]['v'])

    def get_date(self):
        """Return the Invoice date."""
        invoice_date = None
        if 'Invoice date' in self.metadata:
            invoice_date = datetime.datetime.strptime(
                self.metadata['Invoice date'],
                '%b %d, %Y'
            ).strftime('%Y-%m-%d')
        elif 'Issue date' in self.metadata:
            invoice_date = datetime.datetime.strptime(
                self.metadata['Issue date'],
                '%b %d, %Y'
            ).strftime('%Y-%m-%d')
        return invoice_date

    def get_id(self):
        """Return the Invoice ID."""
        if self.type == 'csv':
            return self.name.replace('.csv', '')
        elif self.type == 'json':
            name = self.name.replace('json/', '')
            name = name.replace('.json', '')
            return name.split(' ')[2]

    def get_object_media(self):
        """Get the object media."""
        # get the object media
        f = self.google.storage().get_object_media(
            self.bucket,
            self.name
        )

        # retrive the string value of the object
        self.objectMedia = f.getvalue()

        # convert the media to data
        if self.type == 'csv':
            self.get_csv_object_media()
        elif self.type == 'json':
            self.get_json_object_media()

    def get_csv_header(self):
        """Return the data from the CSV header section."""
        lines = self.sections[0].split('\n')
        fieldnames = ['key', 'value']
        csvreader = csv.DictReader(lines, fieldnames=fieldnames)
        header = {}
        for line in csvreader:
            key = line['key']
            header[key] = line['value']
        return header

    def get_csv_lines(self):
        """Return a list of lines from a CSV DictReader."""
        # additional sections
        additional = self.sections[1:]
        lines = []
        for section in additional:
            lines.extend(self.get_csv_section_lines(section))
        return lines

    def get_csv_object_media(self):
        """Retrieve the data from a GCS CSV object."""
        # parse the csv object media into sections
        self.sections = self.get_csv_sections()

        # get the header data from the first section
        self.header = self.get_csv_header()

        # get the invoice lines from the other sections
        self.lines = self.get_csv_lines()

        # set the line count
        self.header['Line count'] = str(len(self.lines))

        # create the data dictionary (equivalent of json file)
        self.data = self.header.copy()
        self.data['lines'] = self.lines

    def get_csv_section_lines(self, section):
        """Return the data from a section of an invoice."""
        return list(csv.DictReader(section.split('\n')))

    def get_csv_sections(self):
        """Return the sections of the CSV file."""
        sections = []
        if sys.version_info < (3, 0):
            self.objectMedia = unicode(self.objectMedia, errors='ignore')
        else:
            self.objectMedia = self.objectMedia.decode('ascii', errors='ignore')
        for section in self.objectMedia.split('\n\n'):
            if section.strip():
                sections.append(section)
        return sections

    def get_json_object_media(self):
        """Retrieve the data from a GCS JSON object."""
        # get data from object media
        self.data = json.loads(self.objectMedia)

        # get header data from data
        self.header = self.data.copy()

        # get lines from data
        self.lines = self.data['lines']

        # set the line count
        self.header['Line count'] = str(len(self.lines))

        # delete the invoice lines from the header
        del self.header['lines']

    def update_all(self, bucket):
        """Update all invoices."""
        # get all GCS objects
        all_invoices = self.from_gcs(bucket)

        # split into csv and json invoices
        csv_invoices = []
        json_invoices = []
        for i in all_invoices:
            if i.type == 'csv':
                csv_invoices.append(i)
            elif i.type == 'json':
                json_invoices.append(i)
            else:
                print('ERROR: Unknown type [%s]: %s' % (i.type, i.name))

        # display details
        print('Objects: %s' % (len(all_invoices)))
        print('  CSV Invoices: %s' % (len(csv_invoices)))
        print('  JSON Invoices: %s' % (len(json_invoices)))

        # update csv invoices
        print('\nUpdating CSV invoices...')
        self.update_csv_invoices(csv_invoices)

        # update json invoices
        print('\nUpdating JSON invoices...')
        self.update_json_invoices(csv_invoices, json_invoices)

    def update_csv_invoices(self, csv_invoices):
        """Update CSV invoices."""
        for i in csv_invoices:
            if self.verbose:
                print(' * %s...' % (i.name))
            # get the data from the object media
            i.get_object_media()
            # check invoice
            i.check_content_type()
            i.check_metadata()

    def update_json_invoices(self, csv_invoices, json_invoices):
        """Update JSON invoices."""
        # get a dict of all csv invoices
        csv_invoices_dict = {}
        for i in csv_invoices:
            csv_invoices_dict[i.id] = i

        # get a dict of all json invoices
        json_invoices_dict = {}
        for i in json_invoices:
            json_invoices_dict[i.id] = i

        # find invoices to add
        for invoice_id in csv_invoices_dict:
            if invoice_id not in json_invoices_dict:
                i = csv_invoices_dict[invoice_id]
                print(' + Add %s' % (invoice_id))
                i.update_object_data()

        # find invoices to delete
        for invoice_id in json_invoices_dict:
            if invoice_id not in csv_invoices_dict:
                i = json_invoices_dict[invoice_id]
                print(' + Delete %s' % (invoice_id))
                i.delete_json_invoice()

        # update all json invoices
        for i in json_invoices:
            if i.id not in csv_invoices_dict:
                continue
            c = csv_invoices_dict[i.id]
            if self.verbose:
                print(' * %s...' % (i.name))
            # get the data from the object media
            i.get_object_media()
            # check invoice
            i.check_content_type()
            i.check_metadata()
            i.check_data(c)

    def update_object_data(self):
        """Update object data."""
        # create the object name
        name = 'json/%s Invoice %s.json' % (
            self.get_date(),
            self.get_id(),
        )

        # create the body of the request
        body = {
            'contentType': 'application/json',
            'metadata': self.header,
            'name': name,
        }

        # create the object media
        objectMedia = json.dumps(self.data)
        if sys.version_info < (3, 0):
            objectMedia = unicode(objectMedia)
        media_body = apihttp.MediaIoBaseUpload(
            StringIO(objectMedia),
            'application/json'
        )

        # re-write object in gcs
        self.storage.objects().insert(
            bucket=self.bucket,
            body=body,
            media_body=media_body,
        ).execute()

    def update_object_metadata(self):
        """Update object metadata."""
        return self.storage.objects().update(
            bucket=self.bucket,
            object=self.name,
            body=self.object,
        ).execute()
