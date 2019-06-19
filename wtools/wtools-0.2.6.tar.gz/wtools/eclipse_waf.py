#! /usr/bin/env python3
# encoding: utf-8
# Eclipse CDT 5.0 generator for Waf
# Richard Quirk 2009-1011 (New BSD License)
# Thomas Nagy 2011 (ported to Waf 1.6)

"""
Usage:

def options(opt):
    opt.load('eclipse')

$ waf configure eclipse
"""

import sys, os, platform, subprocess
from waflib import Utils, Logs, Context, Build, TaskGen, Scripting
from xml.dom.minidom import Document

from waflib import Logs

STANDARD_INCLUDES = [ '/usr/local/include', '/usr/include', '/usr/lib/gcc/x86_64-linux-gnu/5/include' ]

OE_CDT      = 'org.eclipse.cdt'
CDT_MK      = 'org.eclipse.cdt.make.core'
CDT_CORE    = 'org.eclipse.cdt.core'
CDT_BLD     = 'org.eclipse.cdt.build.core'


def options(opt):
    opt.add_option('--eclipse-install', dest='eclipse_default_install', 
        default=False, action='store_true', help='use install as default eclipse command')    
    opt.add_option('--eclipse-preserve', dest='eclipse_preserve_project', 
        default=False, action='store_true', help='do not overwrite existing eclipse project files')    
    opt.add_option('--eclipse-projects', dest='eclipse_projects', 
        default=None, help='comma separated list of eclipse project dependencies')


def configure(conf):
    if conf.options.eclipse_default_install:
        conf.env.ECLIPSE_DEFAULT_INSTALL = [1]
    if conf.options.eclipse_preserve_project:
        conf.env.ECLIPSE_PRESERVE_PROJECT = [1]
    if conf.options.eclipse_projects:
        conf.env.ECLIPSE_PROJECTS = conf.options.eclipse_projects.split(',')


class eclipse(Build.BuildContext):
    cmd = 'eclipse'
    fun = Scripting.default_cmd

    def execute(self):
        """
        Entry point
        """
        self.restore()
        if not self.all_envs:
            self.load_envs()
        self.recurse([self.run_dir])

        appname = getattr(Context.g_module, Context.APPNAME, os.path.basename(self.srcnode.abspath()))
        self.create_cproject(appname, pythonpath=self.env['ECLIPSE_PYTHON_PATH'])

    def get_cpppath(self):
        cpppath = self.env['CPPPATH']

        if not sys.platform.startswith("linux"):
            return cpppath

        cpppath += STANDARD_INCLUDES

        if self.env.DEST_CPU == platform.processor():
            return cpppath
        
        try:
            cmd="%s -print-prog-name=cc1" % self.env.CC[0]
            res = subprocess.check_output(cmd.split())
            res = res.decode('utf-8')
            cmd="echo | %s -v" % (res.split()[0])
            res = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            res = res.decode('utf-8')

            cpppath.extend([l.strip() for l in res.splitlines() if l.startswith(" /")])
        except:
            Logs.debug("get_cpppath: failed to get native CC include search directories")

        if os.path.exists('gccdump.s'):
            try:
                os.remove('gccdump.s')
            except:
                Logs.debug("get_cpppath: failed to remove gccdump.s")

        cpppath.extend(Utils.to_list(self.env.SYSROOT))

        for cflag in self.env.CFLAGS:
            if cflag.startswith('-I'):
                cpppath.append(cflag.lstrip('-I'))

        cpppath = list(set(cpppath))
        return cpppath


    def get_cpp_defines(self):
        if 'win32' in sys.platform:
            return []

        cxx = self.env.CXX[0]
        res = subprocess.check_output(['%s -dM -E - < /dev/null' % cxx], shell=True, stderr=subprocess.STDOUT)
        defines = res.decode('utf-8').splitlines()
        defines = [d.lstrip('#define ') for d in defines]
        defines = [d.replace(" ", "=", 1) for d in defines]
        return defines


    def get_gcc_defines(self):
        if 'win32' in sys.platform:
            return []

        cc = self.env.CC[0]
        res = subprocess.check_output(['%s -dM -E - < /dev/null' % cc], shell=True, stderr=subprocess.STDOUT)
        defines = res.decode('utf-8').splitlines()
        defines = [d.lstrip('#define ') for d in defines]
        defines = [d.replace(" ", "=", 1) for d in defines]
        return defines


    def create_cproject(self, appname, includes=[], pythonpath=[]):
        """
        Create the Eclipse CDT .project and .cproject files
        @param appname The name that will appear in the Project Explorer
        @param build The BuildContext object to extract includes from
        @param includes Optional project includes to prevent
              "Unresolved Inclusion" errors in the Eclipse editor
        @param pythonpath Optional project specific python paths
        """
        sources = []

        cpppath = self.get_cpppath()

        Logs.warn('Generating Eclipse CDT project files')

        for g in self.groups:
            for tg in g:
                if not isinstance(tg, TaskGen.task_gen):
                    continue

                tg.post()
                if not getattr(tg, 'link_task', None):
                    continue

                features = Utils.to_list(getattr(tg, 'features', ''))

                is_cc = 'c' in features or 'cxx' in features

                incnodes = tg.to_incnodes(tg.to_list(getattr(tg, 'includes', [])) + tg.env['INCLUDES'])
                for p in incnodes:
                    path = p.path_from(self.srcnode)
                    includes.append(path)

                    if is_cc and path not in sources:
                        sources.append(path)

        if self.options.eclipse_preserve_project or self.env.ECLIPSE_PRESERVE_PROJECT:
            for f in ('.project', '.cproject', '.pydevproject'):
                if self.srcnode.find_node('.project'):
                    Logs.warn("preserving existing %s file, skipping export" % f)
                    return

        project = self.impl_create_project(sys.executable, appname)
        self.srcnode.make_node('.project').write(project.toprettyxml())

        waf = os.path.abspath(sys.argv[0])
        project = self.impl_create_cproject(sys.executable, waf, appname, includes, cpppath, sources)
        self.srcnode.make_node('.cproject').write(project.toprettyxml())

        project = self.impl_create_pydevproject(appname, sys.path, pythonpath)
        self.srcnode.make_node('.pydevproject').write(project.toprettyxml())

        cdt_core_prefs = self.impl_create_cdt_core_prefs()
        settings = self.srcnode.make_node(".settings")
        settings.mkdir()
        settings.make_node('org.eclipse.cdt.core.prefs').write(cdt_core_prefs)

    def impl_create_project(self, executable, appname):
        doc = Document()
        projectDescription = doc.createElement('projectDescription')
        self.add(doc, projectDescription, 'name', appname)
        self.add(doc, projectDescription, 'comment')

        projects = self.add(doc, projectDescription, 'projects')
        for proj in [p for p in self.env.ECLIPSE_PROJECTS if p != '']:
            self.add(doc, projects, 'project', proj)

        buildSpec = self.add(doc, projectDescription, 'buildSpec')
        buildCommand = self.add(doc, buildSpec, 'buildCommand')
        self.add(doc, buildCommand, 'name', OE_CDT + '.managedbuilder.core.genmakebuilder')
        self.add(doc, buildCommand, 'triggers', 'clean,full,incremental,')
        arguments = self.add(doc, buildCommand, 'arguments')
        # the default make-style targets are overwritten by the .cproject values
        dictionaries = {
                CDT_MK + '.contents': CDT_MK + '.activeConfigSettings',
                CDT_MK + '.enableAutoBuild': 'false',
                CDT_MK + '.enableCleanBuild': 'true',
                CDT_MK + '.enableFullBuild': 'true',
                }
        for k, v in dictionaries.items():
            self.addDictionary(doc, arguments, k, v)

        natures = self.add(doc, projectDescription, 'natures')
        nature_list = """
            core.ccnature
            managedbuilder.core.ScannerConfigNature
            managedbuilder.core.managedBuildNature
            core.cnature
        """.split()
        for n in nature_list:
            self.add(doc, natures, 'nature', OE_CDT + '.' + n)

        self.add(doc, natures, 'nature', 'org.python.pydev.pythonNature')

        doc.appendChild(projectDescription)
        return doc

    def impl_create_cproject(self, executable, waf, appname, includes, cpppath, sources=[]):
        doc = Document()
        doc.appendChild(doc.createProcessingInstruction('fileVersion', '4.0.0'))
        cconf_id = CDT_CORE + '.default.config.1'
        cproject = doc.createElement('cproject')
        storageModule = self.add(doc, cproject, 'storageModule',
                {'moduleId': CDT_CORE + '.settings'})

        cconf = self.add(doc, storageModule, 'cconfiguration', {'id':cconf_id})

        storageModule = self.add(doc, cconf, 'storageModule',
                {'buildSystemId': OE_CDT + '.managedbuilder.core.configurationDataProvider',
                 'id': cconf_id,
                 'moduleId': CDT_CORE + '.settings',
                 'name': 'Default'})

        self.add(doc, storageModule, 'externalSettings')

        extensions = self.add(doc, storageModule, 'extensions')
        extension_list = """
            VCErrorParser
            MakeErrorParser
            GCCErrorParser
            GASErrorParser
            GLDErrorParser
        """.split()
        self.add(doc, extensions, 'extension', {'id': CDT_CORE + '.ELF', 'point':CDT_CORE + '.BinaryParser'})
        for e in extension_list:
            self.add(doc, extensions, 'extension', {'id': CDT_CORE + '.' + e, 'point':CDT_CORE + '.ErrorParser'})

        storageModule = self.add(doc, cconf, 'storageModule',
                {'moduleId': 'cdtBuildSystem', 'version': '4.0.0'})
        config = self.add(doc, storageModule, 'configuration',
                    {'artifactName': appname,
                     'id': cconf_id,
                     'name': 'Default',
                     'parent': CDT_BLD + '.prefbase.cfg'})
        folderInfo = self.add(doc, config, 'folderInfo',
                            {'id': cconf_id+'.', 'name': '/', 'resourcePath': ''})

        toolChain = self.add(doc, folderInfo, 'toolChain',
                {'id': CDT_BLD + '.prefbase.toolchain.1',
                 'name': 'No ToolChain',
                 'resourceTypeBasedDiscovery': 'false',
                 'superClass': CDT_BLD + '.prefbase.toolchain'})

        self.add(doc, toolChain, 'targetPlatform', {'binaryParser': 'org.eclipse.cdt.core.ELF', 'id': CDT_BLD + '.prefbase.toolchain.1', 'name': ''})

        if self.options.eclipse_default_install or self.env.ECLIPSE_DEFAULT_INSTALL:
            cmd = "install"
        else:
            cmd = eclipse.fun

        Logs.info("eclipse default command: %s" % cmd)

        # detect top level directory; might be different from appname
        try:
            topdir = os.path.basename(self.srcnode.abspath())
        except:
            topdir = appname

        waf_build = '"%s" %s'%(waf, cmd)
        waf_clean = '"%s" clean'%(waf)
        builder = self.add(doc, toolChain, 'builder',
                    {'autoBuildTarget': waf_build,
                     'command': executable,
                     'enableAutoBuild': 'false',
                     'cleanBuildTarget': waf_clean,
                     'enableIncrementalBuild': 'true',
                     'id': CDT_BLD + '.settings.default.builder.1',
                     'incrementalBuildTarget': waf_build,
                     'managedBuildOn': 'false',
                     'name': 'Gnu Make Builder',
                     'superClass': CDT_BLD + '.settings.default.builder'})

        outputEntries = self.add(doc, builder, 'outputEntries')
        self.add(doc, outputEntries, 'entry', {
            'excluding' : "out/|ext/out/|%s/out" % topdir,
            'flags' : "VALUE_WORKSPACE_PATH",
            'kind' : "outputPath",
            'name' : ""
        })

        tools = (
            ("Assembly" , CDT_CORE + '.language.gcc', '.123'),
            ("GNU C++"  , CDT_CORE + '.language.cpp', '.234'),
            ("GNU C"    , CDT_CORE + '.language.gcc', '.345'),
        )

        for (name, language, ti) in tools:
            sc = CDT_BLD + '.settings.holder'
            tool = self.add(doc, toolChain, 'tool', {'id': sc + ti, 'name': name, 'superClass': sc})

            includes = list(set(includes + cpppath))
            if len(includes):
                headers = []
                home = os.path.expanduser("~")
                prefix = self.env.PREFIX
                bld = self.bldnode.abspath()

                for inc in includes:
                    c = os.getcwd()
                    i = os.path.abspath(inc)
                    t = os.path.dirname(c)

                    # REMARK: assume workspace is one level above current project (cwd)
                    if i.startswith(prefix):
                        continue
                    elif i.startswith(bld):
                        continue
                    elif i.startswith(c):
                        val = "${workspace_loc:/%s/%s}" % (topdir, inc)
                    elif i.startswith(t):
                        val = "${workspace_loc:/%s}" % (i.lstrip(t))
                    elif i.startswith(home):
                        val = "%s" % (i.replace(home, '${HOME}', 1))
                    else:
                        val = "%s" % (i)

                    headers.append(val)

                headers = list(set(headers))
                if len(headers):
                    sc = 'org.eclipse.cdt.build.settings.holder.incpaths'
                    option = self.add(doc, tool, 'option',
                        {'id': sc + ti, 'name': 'Include Paths', 'superClass': sc, 'valueType': 'includePath'})

                    for hdr in headers:
                        self.add(doc, option, 'listOptionValue', {'builtIn': 'false', 'value': '"%s"'%(hdr)})

            sc = 'org.eclipse.cdt.build.core.settings.holder.symbols'
            option = self.add(doc, tool, 'option', {'id': sc + ti, 'superClass': sc, 'valueType': 'definedSymbols'})
            for d in self.env.DEFINES:
                self.add(doc, option, 'listOptionValue', { 'builtIn': 'false', 'value': '%s' % d })

            if language.endswith('.cpp'):
                defines = self.get_cpp_defines()
            else:
                defines = self.get_gcc_defines()

            for d in defines:
                self.add(doc, option, 'listOptionValue', { 'builtIn': 'false', 'value': '%s' % d })

            self.add(doc,tool,'inputType',{ 'id':'org.eclipse.cdt.build.core.settings.holder.inType' + ti,
                'languageId':language,'languageName':name,
                'sourceContentType':'org.eclipse.cdt.core.cSource,org.eclipse.cdt.core.cHeader',
                'superClass':'org.eclipse.cdt.build.core.settings.holder.inType' })

        if sources:
            home = os.path.expanduser("~")
            prefix = self.env.PREFIX
            bld = self.bldnode.abspath()

            sourceEntries = self.add(doc, config, 'sourceEntries')
            for src in sources:
                c = os.getcwd()
                s = os.path.abspath(src)
                t = os.path.dirname(c)

                # REMARK: assume workspace is one level above current project (cwd)
                if s.startswith(prefix):
                    continue
                if s.startswith(bld):
                    continue
                elif s.startswith(c):
                    entry = { 'flags':'VALUE_WORKSPACE_PATH|RESOLVED', 'kind':'sourcePath', 'name': "%s" % (src) }
                elif s.startswith(t):
                    continue

                elif s.startswith(home):
                    continue

                else:
                    continue

                self.add(doc, sourceEntries, 'entry', entry)

        storageModule = self.add(doc, cconf, 'storageModule',
                            {'moduleId': CDT_MK + '.buildtargets'})
        buildTargets = self.add(doc, storageModule, 'buildTargets')
        def addTargetWrap(name, runAll):
            return self.addTarget(doc, buildTargets, executable, name,
                                '"%s" %s'%(waf, name), runAll)
        addTargetWrap('configure', True)
        addTargetWrap('dist', False)
        addTargetWrap('install', False)
        addTargetWrap('check', False)

        projects = [p for p in self.env.ECLIPSE_PROJECTS if p != '']
        if len(projects):
            storageModule = self.add(doc, cconf, 'storageModule',
                            {'moduleId': CDT_CORE + ".externalSettings"})
        
            self.add(doc, storageModule, 'externalSettings', 
                    {'containerId':';'.join(projects)+';', 'factoryId':CDT_CORE+'.cfg.export.settings.sipplier'})

        storageModule = self.add(doc, cproject, 'storageModule',
                            {'moduleId': 'cdtBuildSystem',
                             'version': '4.0.0'})

        self.add(doc, storageModule, 'project', {'id': '%s.null.1'%appname, 'name': appname})

        doc.appendChild(cproject)
        return doc

    def impl_create_pydevproject(self, appname, system_path, user_path):
        # create a pydevproject file
        doc = Document()
        doc.appendChild(doc.createProcessingInstruction('eclipse-pydev', 'version="1.0"'))
        pydevproject = doc.createElement('pydev_project')
        prop = self.add(doc, pydevproject,
                       'pydev_property',
                       'python %d.%d'%(sys.version_info[0], sys.version_info[1]))
        prop.setAttribute('name', 'org.python.pydev.PYTHON_PROJECT_VERSION')
        prop = self.add(doc, pydevproject, 'pydev_property', 'Default')
        prop.setAttribute('name', 'org.python.pydev.PYTHON_PROJECT_INTERPRETER')
        # add waf's paths
        wafadmin = [p for p in system_path if p.find('wafadmin') != -1]
        if wafadmin:
            prop = self.add(doc, pydevproject, 'pydev_pathproperty',
                    {'name':'org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH'})
            for i in wafadmin:
                self.add(doc, prop, 'path', i)
        if user_path:
            prop = self.add(doc, pydevproject, 'pydev_pathproperty',
                    {'name':'org.python.pydev.PROJECT_SOURCE_PATH'})
            for i in user_path:
                self.add(doc, prop, 'path', '/'+appname+'/'+i)

        doc.appendChild(pydevproject)
        return doc

    def impl_create_cdt_core_prefs(self):
        template='''eclipse.preferences.version=1
environment/project/org.eclipse.cdt.core.default.config.1/PATH/delimiter=\:
environment/project/org.eclipse.cdt.core.default.config.1/PATH/operation=replace
environment/project/org.eclipse.cdt.core.default.config.1/PATH/value=%s
environment/project/org.eclipse.cdt.core.default.config.1/append=true
environment/project/org.eclipse.cdt.core.default.config.1/appendContributed=true'''
        paths = os.environ['PATH']
        paths = [p for p in set(paths.split(':')) if os.path.exists(p)]
        return template % '\\:'.join(paths)

    def addDictionary(self, doc, parent, k, v):
        dictionary = self.add(doc, parent, 'dictionary')
        self.add(doc, dictionary, 'key', k)
        self.add(doc, dictionary, 'value', v)
        return dictionary

    def addTarget(self, doc, buildTargets, executable, name, buildTarget, runAllBuilders=True):
        target = self.add(doc, buildTargets, 'target',
                        {'name': name,
                         'path': '',
                         'targetID': OE_CDT + '.build.MakeTargetBuilder'})
        self.add(doc, target, 'buildCommand', executable)
        self.add(doc, target, 'buildArguments', None)
        self.add(doc, target, 'buildTarget', buildTarget)
        self.add(doc, target, 'stopOnError', 'true')
        self.add(doc, target, 'useDefaultCommand', 'false')
        self.add(doc, target, 'runAllBuilders', str(runAllBuilders).lower())

    def add(self, doc, parent, tag, value = None):
        el = doc.createElement(tag)
        if (value):
            if type(value) == type(str()):
                el.appendChild(doc.createTextNode(value))
            elif type(value) == type(dict()):
                self.setAttributes(el, value)
        parent.appendChild(el)
        return el

    def setAttributes(self, node, attrs):
        for k, v in attrs.items():
            node.setAttribute(k, v)

