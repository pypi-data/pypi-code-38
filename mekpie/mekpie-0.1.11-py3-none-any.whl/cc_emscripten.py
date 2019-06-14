from .definitions import CompilerConfig, CompilerConfig
from .runner      import autodetect
from .cli         import cli_config, ask, tell

def emscripten():

    def cc_once(cfg):
        lib_flags     = ['-l' + lib for lib in cfg.libs]
        include_flags = ['-I' + inc for inc in cfg.includes]
        return cfg.flags + cfg.compileflags + cfg.linkflags + include_flags + lib_flags
    
    def cc_compile(cfg, source):
        return source

    def cc_link(cfg, main, objects):
        path = cfg.targetpath(main) + '.js'
        cfg.run([
            'emcc',
            main,
            *objects,
            *cfg.once,
            '-o', path,
        ])
        return path

    def cc_run(cfg, exe):
        cfg.run(['node', exe, *cfg.options.programargs])

    def cc_debug(cfg, exe):
        cfg.run(['node', 'inspect', exe])

    return CompilerConfig(
        name         = 'emscripten',
        compile      = cc_compile,
        link         = cc_link,
        run          = cc_run,
        debug        = cc_debug,
        once         = cc_once,
        ccsource     = f'emscripten()',
        flags        = ['-Wall'],
        debugflags   = ['-g'],
        releaseflags = ['-O'],
    )

@cli_config('emscripten')
def config_emscripten():
    return emscripten()