from jsonapi_client import Session, Filter, ResourceTuple
import requests


class connection():
    def __init__(self, url="http://localhost:4000", namespace="api"):
        self.url = url
        self.namespace = namespace

    def connect(self):
        models_schema = {
            'job_scripts': {
                'properties': {
                    'title': {'type': 'string'},
                    'language': {'type': 'string'},
                    'code': {'type': 'string'},
                    'path': {'type': 'string'},
                    'defined-at-runtime': {'type': 'boolean'},
                    'code-strategy': {'type': 'string'}
                }
            },
            'job_templates': {
                'properties': {
                    'title': {'type': 'string'},
                    'user-params': {
                        'type': 'object',
                        'properties': {
                            'interscity': {
                                'type': 'object',
                                'properties': {
                                    'capability': {'type': 'string'},
                                    'sql_queries': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'define-schema-at-runtime': {'type': 'boolean'},
                    'job-script': {'relation': 'to-one', 'resource': ['job-script']}
                }
            },
            'processing_jobs': {
                'properties': {
                    'uuid': {'type': 'string'},
                    'job-state': {'type': 'string'},
                    'log': {'type': 'string'},
                    'job-template': {'relation': 'to-one', 'resource': ['job-template']}
                }
            }
        }
        self.session = Session(self.url + "/api", schema=models_schema)
        script = self.session.create('job_scripts')
        script.title = "SQL Query Script (created by client)"
        script.language = "python"
        script.code = "empty"
        script.path = "interscity_sql_script.py"
        script.defined_at_runtime = True
        script.code_strategy = "Elixir.DataProcessorBackend.InterSCity.ScriptSamples.SqlQuery"
        script.commit()
        self.script_id = script.id

    def sql(self, queries, capability):
        template = self.session.create('job_templates')
        template.title = "SQL Query Template - Created by client"
        template.user_params = {
        'schema': '',
            'functional': '',
            'interscity': {
                'capability': capability,
                'sql_queries': queries
            }
        }
        template.define_schema_at_runtime=True
        template.job_script_id=self.script_id
        template.commit()
        template_id = template.id
        hd = {'Accept': 'application/vnd.api+json', 'Content-Type': 'application/vnd.api+json'}
        endpoint = self.url + "/api/job_templates/{0}/schedule".format(template_id)
        r = requests.post(endpoint, headers=hd)
        job_id = r.json()['data']['id']
        return job_id

    def process(self, job_id):
        endpoint = self.url + '/api/processing_jobs/{0}/run'.format(job_id)
        hd = {'Accept': 'application/vnd.api+json', 'Content-Type': 'application/vnd.api+json'}
        print("Running job...")
        r = requests.post(endpoint, json={'processing_job_id': 2}, headers=hd)
        print("Done! Response:")
        return r
