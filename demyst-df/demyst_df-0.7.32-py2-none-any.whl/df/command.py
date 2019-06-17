#!/usr/bin/env python3

import os
import sys
import json
import click
import datetime
import requests
import boto3
import botocore
import zipfile
import time
from urllib.parse import urlparse
from tabulate import tabulate
from halo import Halo
import io
import distutils
from distutils import dir_util

# Automated testing
import unittest

from demyst.common.config import load_config

# https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries
from zipfile import ZipFile, ZipInfo
class MyZipFile(ZipFile):
    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)
        if path is None:
            path = os.getcwd()
        ret_val = self._extract_member(member, path, pwd)
        attr = member.external_attr >> 16
        if(attr > 0):
            os.chmod(ret_val, attr)
        return ret_val


DFUNC = lambda x: {"test": False}

def debug(*strs):
    wants_debug = os.getenv("DEBUG", False)
    if wants_debug:
        print(*strs)

class TestFunction(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.event = {
            "input": {
                "pass_through": {
                    "data": {
                        "email_address": "test@test.com"
                    }
                }
            }
        }

    def test_it(self):
        resp = DFUNC(self.event)

    def test_break_all_providers(self):
        os.environ["DEMYST_DF_PROVIDER_ERROR"] = "true"
        resp = DFUNC(self.event)

def stress_test(inputs=None):
    if inputs is None:
        inputs = {}
    sys.path.insert(0, os.getcwd())
    function_dir = os.getcwd() + "/function"
    debug("Function dir in stress_test", function_dir)
    sys.path.insert(0, function_dir)
    import function
    TestFunction.DFUNC = function.data_function
    suite = unittest.TestSuite()
    suite.addTest(TestFunction('test_it'))
    suite.addTest(TestFunction('test_break_all_providers'))
    test_out = io.StringIO()
    result = unittest.TextTestRunner(test_out).run(suite)
    if (len(result.errors) > 0 or len(result.failures) > 0):
        print(test_out.getvalue())
        return False
    return True

@click.group()
def cli():
    pass

# XXX Add inputs.json for testing inputs missing as well.
@cli.command()
def test():
    spinner = Halo(text='Testing Data Function ...', spinner='dots', stream=sys.stderr)
    spinner.start()

    if (not stress_test()):
        spinner.fail("Testing resulted in failures")
        return -1
    else:
        spinner.succeed("Successfully completed testing")
        return 0

@cli.command()
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
def watch(env, region):
    spinner = Halo(text='Connecting to logging service ...', spinner='dots')
    spinner.start()

    c = load_config(env=env, region=region)
    murl = ("%sdata_functions/%s/tail_log_credentials?api_key=%s"
            % (c.get("MANTA_URL"),
               c.get("DATA_FUNCTION_ID"),
               c.get("API_KEY")))
    response = requests.get(murl)
    if (response.status_code != 200):
        spinner.fail("Failed to authenticate using MANTA_URL, DATA_FUNCTION_ID & API_KEY")
        return -1

    creds = response.json()
    cwlogs = boto3.client('logs',
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
        aws_session_token=creds["session_token"],
    )
    bad_strings = ["START RequestId", "END RequestId", "REPORT RequestId"]
    res = cwlogs.filter_log_events(logGroupName="/aws/lambda/%s"%(c.get("DATA_FUNCTION_NAME")))
    messages = map(lambda x: [x["timestamp"], x["message"]], res["events"])
    valid_messages = list(filter(lambda m: not any(x in m[1] for x in bad_strings), messages))
    spinner.succeed("Successfully fetched latest Data Function logs:")
    for m in valid_messages:
        t = int(m[0]) / 1000.0
        ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S.%f')
        print("%s - %s"%(ts, m[1].rstrip()))

@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file for Data Function or ./df.config')
@click.option('--channel_id', required=True, help='Request channel ID')
@click.option('--inputs_file', required=True, help='JSON inputs file (see inputs.example.json)')
@click.option('--sample_mode', is_flag=True, help='Run providers in sample mode.')
@click.option('--pipes_only', is_flag=True, help='Only display pipe (data function) results.')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
def channel(config_file, channel_id, inputs_file, sample_mode, pipes_only, env, region):
    spinner = Halo(text='Connecting to Demyst API ...', spinner='dots', stream=sys.stderr)
    spinner.start()
    c = load_config(config_file=config_file, env=env, region=region)
    if not (os.path.isfile(inputs_file)):
        spinner.fail("Couldn't read input file (%s)"%(inputs_file))
        return -1

    str = open(inputs_file, "r").read()
    inputs = json.loads(str)

    post = {
        "api_key": c.get("API_KEY"),
        "id": channel_id,
        "inputs": inputs
    }
    if (sample_mode):
        post['config'] = {'mode': 'sample'}

    channel_url = c.get("BLACKFIN_URL") + "v2/channel"
    resp = requests.post(channel_url,
                         data = json.dumps(post),
                         headers={'Content-Type':'application/json'})
    if (resp.status_code != 200):
        reason = resp.json()["error"]["message"]
        spinner.fail("Failure: %s"%(reason))
        return -1
    spinner.succeed("Successfully requested channel:")

    if (pipes_only):
        j = resp.json()
        pipes = j.get("pipes", "{}")
        print(json.dumps(pipes, indent=2, sort_keys=True))
    else:
        print(resp.text)

@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file for Data Function or ./df.config')
@click.option('--pipe_id', default=None, required=False, help='Only print details for a single Pipe')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
def list_pipes(config_file, pipe_id, env, region, spinner=None):
    if spinner == None:
        spinner = Halo(text='Requesting pipes ...', spinner='dots', stream=sys.stderr)
    spinner.start()

    c = load_config(config_file=config_file, env=env, region=region)
    murl = ("%sdata_functions/pipes.json?api_key=%s"
            %(c.get("MANTA_URL"),
              c.get("API_KEY")))
    response = requests.get(murl)

    if (response.status_code != 200):
        spinner.fail("Failed to authenticate using MANTA_URL & API_KEY")
        return -1

    pipes = response.json()
    ids = pipes.keys()

    headers = ["ID", "Active?", "Pipe Name", "Channel ID", "Data Function"]
    table = []
    for id in ids:
        if (pipe_id != None and int(pipe_id) != int(id)):
            continue
        pipe = pipes[id]
        table.append([pipe['id'], pipe['active'], pipe['name'], pipe['channel_id'], pipe['df_name']])

    spinner.succeed("Successfully fetched pipes:")
    print("")
    print(tabulate(table, headers, tablefmt="presto"))
    print("")
    return 0

@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file for Data Function or ./df.config')
@click.option('--pipe_id', default=None, required=True, help='Pipe to associate DF to')
@click.option('--data_function_id', default=None, required=False, help='DF to associate Pipe to (Defaults to Data Function found in config).')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
@click.pass_context
def attach_pipe(ctx, config_file, pipe_id, data_function_id, env, region, spinner=None):
    if spinner == None:
        spinner = Halo(text='Attaching Data Function to pipe ...', spinner='dots', stream=sys.stderr)
    spinner.start()
    c = load_config(config_file=config_file, env=env, region=region)

    if (data_function_id == None):
        data_function_id = c.get("DATA_FUNCTION_ID")
    post = {
        "pipe_id": int(pipe_id),
        "data_function_id": int(data_function_id),
        "api_key": c.get("API_KEY")
    }
    murl = ("%sdata_functions/add_data_function_to_pipe"%(c.get("MANTA_URL")))
    response = requests.post(murl,
                         data = json.dumps(post),
                         headers={'Content-Type':'application/json'})
    if (response.status_code != 200):
        spinner.fail("Failed to authenticate using MANTA_URL & API_KEY")
        return -1

    spinner.succeed("Successfully attached Data Function %s to Pipe %s"%(data_function_id, pipe_id))
    ctx.invoke(list_pipes, config_file=config_file, pipe_id=pipe_id, spinner=spinner, env=env, region=region)
    return 0

@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file for Data Function or ./df.config')
@click.option('--pipe_id', default=None, required=True, help='Pipe to detach Data Functions from.')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
@click.pass_context
def detach_pipe(ctx, config_file, pipe_id, env, region, spinner=None):
    if spinner == None:
        spinner = Halo(text='Detaching Data Function to pipe ...', spinner='dots', stream=sys.stderr)
    spinner.start()

    c = load_config(config_file=config_file, env=env, region=region)

    post = {
        "pipe_id": int(pipe_id),
        "api_key": c.get("API_KEY")
    }
    murl = ("%sdata_functions/add_data_function_to_pipe"%(c.get("MANTA_URL")))

    if c.settings["REGION"] == 'local':
        response = requests.post(murl,
                                 data = json.dumps(post),
                                 headers={'Content-Type':'application/json'},
                                 verify=False
        )
    else:
        response = requests.post(murl,
                                 data = json.dumps(post),
                                 headers={'Content-Type':'application/json'}
        )


    if (response.status_code != 200):
        spinner.fail("Failed to authenticate using MANTA_URL & API_KEY")
        return -1

    spinner.succeed("Successfully detached Data Function from Pipe %s"%(pipe_id))
    ctx.invoke(list_pipes, config_file=config_file, pipe_id=pipe_id, spinner=spinner, env=env, region=region)
    return 0

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == 'function.zip':
                debug("Skipping ", file)
                continue
            debug("Zipping File: ", file)
            ziph.write(os.path.join(root, file))

@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file or ./df.config')
@click.pass_context
def tile_json(ctx, config_file, spinner=None):
    if spinner == None:
        spinner = Halo(text='Creating tile json file ...', spinner='dots', stream=sys.stderr)
    sys.path.insert(0, './function')
    import definition
    result_dict = definition.tile_data()
    with open('data_function.json', 'w') as outfile:
        json.dump(result_dict, outfile, indent=4, separators=(',', ': '), sort_keys=True)
    spinner.succeed("Successfully created tile json")
    return 0


@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file or ./df.config')
@click.pass_context
def artifact(ctx, config_file, spinner=None):
    if spinner == None:
        spinner = Halo(text='Creating deployable artifact ...', spinner='dots', stream=sys.stderr)

    function_zip_path = './function.zip'

    if os.path.exists(function_zip_path):
        os.remove(function_zip_path)
    else:
        debug("The ./function.zip does not exist")

    zipf = zipfile.ZipFile(function_zip_path, 'w', zipfile.ZIP_DEFLATED)

    # create data_function.json file from the function.py file where required inputs etc. are defined
    ctx.invoke(tile_json, config_file=config_file, spinner=spinner)

    zipdir('./', zipf)
    zipf.close()
    spinner.succeed("Successfully created deployable artifact")
    return 0



@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file or ./df.config')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
@click.pass_context
def deploy(ctx, config_file, env, region):
    c = load_config(config_file=config_file, env=env, region=region)

    spinner = Halo(text='Loading', spinner='dots', stream=sys.stderr)

    spinner.start("Stress testing data function ...")
    if (not stress_test()):
        spinner.fail("Deployment failed as a result of stress test failures")
        return -1

    spinner.start("Creating deployable artifact ...")
    ctx.invoke(artifact, config_file=config_file, spinner=spinner)

    post = {
        "id": c.get("DATA_FUNCTION_ID"),
    }
    debug("post", post)
    murl = ("%sdata_functions/deploy_url"%(c.get("MANTA_URL")))
    debug("Murl", murl)


    ### Do not start spinner before this first auth_post
    ### If the user does not have a JWT or API_KEY then the spinner
    ### swallows the prompt for username + password
    ### Start Spinner after this first auth_post call.
    response = c.auth_post(murl, data = json.dumps(post), headers={'Content-Type':'application/json'})
    debug("response", response.text)

    if (response.status_code != 200):
        spinner.fail("Failed to authenticate using MANTA_URL, DATA_FUNCTION_ID & API_KEY")
        print(response.text)
        print(response.status_code)
        return -1

    deploy_url = response.json()["presigned_url"]

    spinner.start("Uploading artifact to deployment service ...")

    urlp = urlparse(deploy_url)
    bucket = urlp.hostname.split('.')[0]
    key = urlp.path[1:]

    files = {'file': open('./function.zip', 'rb')}
    response = requests.put(deploy_url, files=files)
    if (response.status_code != 200):
        spinner.fail("Failed to upload Data Function to deployment service")
        return -1

    spinner.succeed("Successfully uploaded Data Function to deployment service")


    # can't have spinner now because if the jwt gets lost and we try to re-auth it'll get swallowed by the spinner
    spinner.start("Checking if deployment is complete ...")
    #    print("Checking if deployment is complete ...")

    for x in range(0, 181):
        murl = ("%sdata_functions/%s/poll_for_complete?api_key=%s&bucket=%s&key=%s"
            %(c.get("MANTA_URL"),
              c.get("DATA_FUNCTION_ID"),
              c.get("API_KEY"),
              bucket,
              key))

        response = c.auth_get(murl)
        payload = response.json()
        if (payload["complete"] and (payload["success"] == True)):
            break
        if (payload["complete"] and (payload["success"] == False)):
            spinner.fail("Failed to deploy Data Function")
            return -1
        if (x > 60):
            spinner.warn("Deployment is taking unusually long")
        if (x >= 180):
            spinner.fail("Deployment timed out")
            return -2
        time.sleep(3)

    spinner.succeed("Successfully deployed Data Function")
    spinner.stop()

    ctx.invoke(post_tile_data, config_file=config_file, env=env, region=region)

    return 0


@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file or ./df.config')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
@click.pass_context
def post_tile_data(ctx, config_file, env, region):
    ### POST TILE_DATA TO MANTA HERE
    # Read the json defining the tile, post to manta
    c = load_config(config_file=config_file, env=env, region=region)

    file = open("./data_function.json", "r")
    tile_data = json.loads(file.read())
    post = {
        "id": c.get("DATA_FUNCTION_ID"),
        "tile_data": tile_data
    }
    murl = ("%sdata_functions/make_tile"%(c.get("MANTA_URL")))
    debug("murl", murl)
    response = c.auth_post(murl, data = json.dumps(post), headers={'Content-Type':'application/json'})
    debug(response.text)

    return 0
    ### End POST TILE_DATA TO MANTA


@cli.command()
@click.argument('name')
@click.argument('path', default='./')
@click.option('--config_file', default=None, required=False, help='Config file or ./df.config')
@click.option('--version', default=2, required=False, help='Version of the Data Function (1 or 2).')
@click.option('--username', default=None, required=False, help='Username.')
@click.option('--password', default=None, required=False, help='Password.')
@click.option('--key', default=None, required=False, help='API key.')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
def create(name, path, version, config_file, env, region, key, username, password):
    c = load_config(config_file=config_file, env=env, region=region, key=key, username=username, password=password)

    here_dir = os.path.dirname(os.path.realpath(__file__))
    dst = os.path.join(path, name)

    if version == 1:
        src = here_dir + "/data/v1/data-function.zip"
        with MyZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dst)
    else:
        src = here_dir + "/data/v2"
        dir_util.copy_tree(src, dst)

    # default to creating data functions in prod
    # possibly create a endpoint to check API_KEY and see if it exists and fall through to stg then dev then local if we want to support other environments ?
    register_url = ("%sdata_functions/register_new" %(c.get("MANTA_URL")))
    response = c.auth_post(register_url, data={'name': name})
    # write response down to file in given directory as df.config
    with open(os.path.join(dst, 'df.config'), 'w') as file:  # Use file to refer to the file object
        file.write(response.text)
        os.chmod(dst, 0o755)
        print("Successfully registered data function")

@cli.command()
@click.option('--config_file', default=None, required=False, help='Config file for Data Function or ./df.config')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
@click.option('--inputs_file', required=True, help='JSON inputs file (see inputs.example.json)')
def execute(config_file, env, region, inputs_file):
    spinner = Halo(text='Executing Data Function locally ...', spinner='dots', stream=sys.stderr)
    spinner.start()

    c = load_config(config_file=config_file, env=env, region=region)

    if not (os.path.isfile(inputs_file)):
        spinner.fail("Couldn't read input file (%s)"%(inputs_file))
        return -1
    str = open(inputs_file, "r").read()
    inputs = json.loads(str)

    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, os.getcwd() + "/function")
    import function

    input_payload = {
        'input': {
            'pass_through': {
                'data': inputs
            }
        }
    }

    import io
    from contextlib import redirect_stdout

    output = ""
    with io.StringIO() as buf, redirect_stdout(buf):
        function.data_function(input_payload)
        output = buf.getvalue()

    spinner.succeed("Execution complete")
    spinner.stop()
    print("\n" + output)
    return 1


if __name__ == '__main__':
    cli()
