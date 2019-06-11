r'''
Usage:
    detk-report generate [options]
    detk-report clean [options]
'''

cmd_opts = {
        'generate':r'''
Usage:
    detk-report generate [options]

Options:
    --dev  Format html for development (larger file size)
''',
        'clean':r'''
Usage:
    detk-report clean [options]
'''
}

from collections import OrderedDict, Mapping
from docopt import docopt
from glob import glob
import hashlib
import jinja2
import json
import logging
from pprint import pformat
import numpy as np
import os
import pathlib
import pkg_resources
import shutil
import sys
import time
import de_toolkit

# for some reason, pkg_resources can't find assets in de_toolkit
# unless I access __path__???!?
de_toolkit.__path__

from .common import _cli_doc, set_logging
from .version import __version__

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16,np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, 
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    def encode(self, obj) :
        if isinstance(obj, float) :
            return format(obj, '.3f').replace('nan','NaN')
        elif isinstance(obj, (list, tuple)) :
            return '['+', '.join(list(map(self.encode, obj)))+']'
        elif isinstance(obj, Mapping) :
            vals = []
            for k in sorted(obj) :
                vals.append('"{}": {}'.format(k,self.encode(obj[k])))
            return '{' + ', '.join(vals) + '}'
        return json.JSONEncoder.encode(self, obj)

def hash_str(st) :
    return hashlib.md5(st.encode()).hexdigest()

class DetkModuleJSON(object):
    def __init__(self,
            module,
            in_file_path=None,
            out_file_path=None,
            column_data_path=None,
            workdir=None,
            json_dir='.',
            json_path=None) :

        # the json filename is calculated as the combination of
        # the module name, the parameters passed, and the input filename
        repl_file_path = '-' if in_file_path is None else in_file_path

        # since the parameters is a dictionary, convert to a json string
        # to calculate the hash
        param_str = json.dumps(module.params, sort_keys=True, cls=NumpyEncoder)
        logger.debug('report param string:\n%s',pformat(param_str))

        module_id = hash_str(module.name+param_str+repl_file_path+__version__)
        logger.debug('writing module for module_id: %s',module_id)

        filename = '{}.json'.format(module_id)

        if json_path is not None :
            self.filepath = json_path
        else :
            self.filepath = os.path.realpath(os.path.join(json_dir,filename))
        logger.debug('writing module JSON to: %s',self.filepath)

        if workdir is None :
            workdir = os.getcwd()

        module_json = module.json
        self.out_d = OrderedDict([
            ('name',module.name),
            ('id',module_id),
            ('detk_version',__version__),
            ('last_modified',int(1000*time.time())),
            ('in_file_path',in_file_path),
            ('out_file_path',out_file_path),
            ('column_data_path',column_data_path),
            ('workdir',workdir),
            ('params',module_json['params']),
            ('properties',module_json['properties'])
        ])

    def write(self,indent=None) :
        '''
        Write out the module JSON to file.

        Each JSON file has one top level object with the following properties:
        - ``name``: name of the module
        - ``id``: machine readable ID
        - ``detk_version``: version of detk that generated this file
        - ``last_modified``: local system timestamp in milliseconds when this
          file was created/modified
        - ``workdir``: path to the directory where detk was run
        - ``in_file_path``: path to the file that was processed
        - ``out_file_path``: path to the file that was output, if available
        - ``column_data_path``: path to the column data file used, if available
        '''

        logger.debug('writing out module JSON for module %s (id: %s)',self.out_d['name'],self.out_d['id'])

        with open(self.filepath,'wt') as f :
            json.dump(self.out_d,f,indent=indent,cls=NumpyEncoder)

def walk(path) :
    l = []
    for tmpl_path in pkg_resources.resource_listdir('de_toolkit',path) :
        tmpl_path = os.path.join(path,tmpl_path)
        if pkg_resources.resource_isdir('de_toolkit',tmpl_path) :
            l.extend(walk(tmpl_path))
        else :
            l.append(tmpl_path)
    return l

class DetkReport(object):
    def __init__(self, report_dir='./detk_report') :
        self.report_dir = os.path.realpath(report_dir)
        logger.debug('creating DetkReport at report dir: %s',self.report_dir)

        self.json_dir = os.path.join(self.report_dir,'json')
        logger.debug('json dir: %s',self.json_dir)

        pathlib.Path(self.json_dir).mkdir(parents=True, exist_ok=True)
        self.report_path = os.path.join(self.report_dir,'detk_report.html')
        logger.debug('report path: %s',self.report_path)

        self.modules = []

        self._template_data = {
                'data':None,
                'common': {},
                'templates': {},
                'assets': {}
                }

    def add_module(self,
            module,
            in_file_path=None,
            out_file_path=None,
            column_data_path=None,
            workdir=None
            ) :
        'Add and serialize the given module to the report directory'
        module_json = DetkModuleJSON(
                module,
                in_file_path=in_file_path,
                out_file_path=out_file_path,
                column_data_path=column_data_path,
                workdir=workdir,
                json_dir=self.json_dir
        )
        logger.debug('adding detk module json for module %s',module.name)
        self.modules.append(module_json)

    @property
    def template_name(self) :
        return 'base.html'

    @property
    def template_data(self) :

        logger.debug('loading report templates')

        template_data = self._template_data

        json_str = self.json

        # loading the whole json object on a single long line is hard on text
        # editors
        template_data['data'] = json.dumps(json_str,cls=NumpyEncoder)

        # format the report
        # do a scan through the json directory to pick up all the existing
        # reports
        module_names = set()
        for module in json_str :
            module_names.add(module.get('name'))

        # load the module templates for the modules found in the report dir
        for asset in ('js','css','html') :
            # common (common) assets
            common_path = 'templates/{}/common.{}'.format(asset,asset)
            if pkg_resources.resource_exists('de_toolkit',common_path) :
                template_data['common'][asset] = \
                    pkg_resources.resource_string('de_toolkit',common_path).decode()

            # module templates
            d = template_data['templates'][asset] = {}
            for name in module_names :
                tmpl_path = 'templates/{}/{}.{}'.format(asset,name,asset)
                if pkg_resources.resource_exists('de_toolkit',tmpl_path) :
                    logger.debug('found template, loading: %s',tmpl_path)
                    template_data['templates'][asset][name] = \
                        pkg_resources.resource_string('de_toolkit',tmpl_path).decode()
                else :
                    logger.debug('no template found, skipping: %s',tmpl_path)

            # third party assets
            template_data['assets'][asset] = {}
            asset_dir = 'templates/{}/assets/'.format(asset)
            if pkg_resources.resource_exists('de_toolkit',asset_dir) :
                for tmpl_path in walk(asset_dir) :
                    logger.debug('loading asset: %s',tmpl_path)
                    template_data['assets'][asset][os.path.basename(tmpl_path)] =  \
                        pkg_resources.resource_string('de_toolkit', tmpl_path).decode()

        return template_data

    @property
    def json(self) :

        logger.debug('collecting report json')

        # write all the module JSON
        for module in self.modules :
            logger.debug('writing module JSON: %s',module.out_d.get('name'))
            module.write()

        # format the report
        # do a scan through the json directory to pick up all the existing
        # reports
        json_str = []
        for fn in glob(os.path.join(self.json_dir,'*.json')) :
            logger.debug('found module json: %s',fn)
            with open(fn) as f :
                j = f.read().strip()
                json_str.append(json.loads(j))

        return json_str

    def write(self) :

        logger.debug('writing out report')

        # write all the module JSON for this report
        for module in self.modules :
            logger.debug('writing module JSON: %s',module.out_d.get('name'))
            module.write()

        # create and render the template
        logger.debug('rendering report template')
        template = jinja2.Template(
            pkg_resources.resource_string(
                'de_toolkit','templates/html/{}'.format(
                    self.template_name
                )
            ).decode()
        )

        with open(self.report_path,'wb') as f :
            logger.debug('writing out template')
            f.write(template.render(**self.template_data).encode())

    def __enter__(self) :
        return self

    def __exit__(self,type,value,traceback):
        self.write()

class DetkReportDev(DetkReport) :
    @property
    def template_name(self) :
        return 'base_dev.html'

    @property
    def template_data(self) :
        template_data = self._template_data
        # in development mode, copy assets and data to the report directory
        # instead of writing into the file

        json_str = self.json

        # write the data into its own javascript file
        data_path = os.path.join(self.json_dir,'data.js')
        template_data['data_path'] = 'json/data.js'
        with open(data_path,'w') as f :
            f.write('var detk = detk || {};')
            f.write('detk.data = {};'.format(
                        json.dumps(json_str,indent=2,cls=NumpyEncoder)
                    )
            )

        # format the report
        # do a scan through the json directory to pick up all the existing
        # reports
        module_names = set()
        for module in json_str :
            module_names.add(module.get('name'))

        # load the module templates for the modules found in the report dir
        for asset in ('js','css','html') :

            logger.debug('preparing %s templates',asset)

            dest_dir = pathlib.Path(os.path.join(self.report_dir,asset))
            dest_dir.mkdir(parents=True, exist_ok=True)

            # common assets
            common_path = 'templates/{}/common.{}'.format(asset,asset)
            logger.debug('looking for common %s template: %s',asset, common_path)
            if pkg_resources.resource_exists('de_toolkit',common_path) :
                logger.debug('found common asset, loading')
                template_data['common'][asset] = \
                    pkg_resources.resource_string('de_toolkit',common_path).decode()
                # copy the asset
                #shutil.copy(
                #    pkg_resources.resource_filename(
                #        'de_toolkit',common_path
                #    ),
                #    os.path.join(self.report_dir,asset,os.path.basename(common_path))
                #)
                # give the relative path to the asset
                #template_data['common'][asset] = '{}/{}'.format(
                #        asset,
                #        os.path.basename(common_path)
                #)

            # module templates, loaded in as in production mode
            d = template_data['templates'][asset] = {}
            for name in module_names :
                tmpl_path = 'templates/{}/{}.{}'.format(asset,name,asset)
                if pkg_resources.resource_exists('de_toolkit',tmpl_path) :
                    template_data['templates'][asset][name] = \
                        pkg_resources.resource_string('de_toolkit',tmpl_path).decode()
            # third party assets, copied as files instead of inserted into the
            # page
            template_data['assets'][asset] = {}
            asset_dir = 'templates/{}/assets/'.format(asset)

            if pkg_resources.resource_isdir('de_toolkit',asset_dir) :

                for tmpl_path in walk(asset_dir) :
                    dest_path_str = tmpl_path.replace('templates/','')
                    dest_path = pathlib.Path(os.path.join(self.report_dir,dest_path_str))
                    logger.debug('copying asset: %s -> %s',tmpl_path,dest_path)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    # copy the asset
                    shutil.copy(
                        pkg_resources.resource_filename('de_toolkit',tmpl_path),
                        str(dest_path)
                    )
                    # give the relative path to the asset
                    #rel_path = tmpl_path.replace('assets/','')
                    #template_data['assets'][asset][rel_path] = dest_path_str

        return template_data

def main(argv=sys.argv) :

    if '--version' in argv :
        from .version import __version__
        print(__version__)
        return

    # add the common opts to the docopt strings
    cmd_opts_aug = {}
    for k,v in cmd_opts.items() :
        cmd_opts_aug[k] = _cli_doc(v)

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmd_opts) :
        docopt(_cli_doc(__doc__))
    argv = argv[1:]
    cmd = argv[0]

    if cmd == 'generate' :
        args = docopt(cmd_opts_aug['generate'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        report_class = DetkReport
        if args['--dev'] :
            logger.info('generating development repot due to --dev')
            report_class = DetkReportDev

        # the context manager loads and writes, do nothing inside
        with report_class(args['--report-dir']) :
            pass

    elif cmd == 'clean' :
        args = docopt(cmd_opts_aug['clean'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        logger.info('cleaning report dir: %s',args['--report-dir'])

        shutil.rmtree(args['--report-dir'],ignore_errors=True)

    logger.info('done')

if __name__ == '__main__' :

    main()
