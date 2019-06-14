from .definitions import CompilerConfig, CompilerConfig
from .runner      import autodetect
from .cli         import cli_config, ask, tell

def gcc_clang(cmd, dbg):

    def cc_once(cfg):
        lib_flags     = ['-l' + lib for lib in cfg.libs]
        include_flags = ['-I' + inc for inc in cfg.includes]
        return {
            'compileflags' : (cfg.flags + include_flags + cfg.compileflags),
            'linkflags'    : (cfg.flags + include_flags + cfg.linkflags + lib_flags),
        }
    
    def cc_compile(cfg, source):
        path = cfg.targetpath(source) + '.o'
        cfg.run([
            cmd, 
            *cfg.once['compileflags'], 
            '-c', source,
            '-o', path
        ])
        return path

    def cc_link(cfg, main, objects):
        path = cfg.targetpath(main)
        cfg.run([
            cmd,
            main,
            *objects,
            *cfg.once['linkflags'],
            '-o', path,
        ])
        return path

    def cc_run(cfg, exe):
        cfg.run([exe, *cfg.options.programargs])

    def cc_debug(cfg, exe):
        cfg.run([dbg, exe])

    return CompilerConfig(
        name         = 'gcc_clang',
        compile      = cc_compile,
        link         = cc_link,
        run          = cc_run,
        debug        = cc_debug,
        once         = cc_once,
        ccsource     = f'gcc_clang(cmd=\'{cmd}\', dbg=\'{dbg}\')',
        flags        = ['-Wall'],
        debugflags   = ['-g'],
        releaseflags = ['-O'],
    )

@cli_config('gcc_clang')
def config_gcc_clang():
    return gcc_clang(
        ask((
            'Please select a compiler command', 
            '',
        ), default=autodetect(['cc', 'gcc', 'clang'])),
        ask((
            'Please select a debug command', 
            ''
        ), default=autodetect(['gdb', 'lldb']))
    )