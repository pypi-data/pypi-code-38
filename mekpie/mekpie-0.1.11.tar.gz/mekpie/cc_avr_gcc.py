from os import name

import shelve

from .definitions import CompilerConfig, CompilerConfig
from .runner      import autodetect
from .cli         import cli_config, ask, tell, panic
from .util        import list_files
from .structure   import get_src_path
from .cache       import quick_cache

MAIN = '''
#include <avr/io.h>
#include <util/delay.h>

int main(void) {
    // !!! THIS WILL ONLY WORK ON SOME DEVICES !!!
    DDRB  = 0xFF;
    PORTB = 0xFF;
    for (;;) {
        PORTB = ~0xFF;  
        _delay_ms(1000);
        PORTB = 0xFF;
        _delay_ms(1000);
    }
    return 0;
}
'''.strip()

hardware_list = [
    'avr1',
    'at90s1200',
    'attiny11',
    'attiny12',
    'avr1',
    'attiny15',
    'attiny28',
    'avr2',
    'at90s2313',
    'at90s2323',
    'at90s2333',
    'at90s2343',
    'attiny22',
    'attiny26',
    'at90s4414',
    'at90s4433',
    'at90s4434',
    'at90s8515',
    'at90c8534',
    'at90s8535',
    'avr25',
    'at86rf401',
    'ata6289',
    'ata5272',
    'ata6616c',
    'attiny13',
    'attiny13a',
    'attiny2313',
    'attiny2313a',
    'attiny24',
    'attiny24a',
    'attiny25',
    'attiny261',
    'attiny261a',
    'attiny4313',
    'attiny43u',
    'attiny44',
    'attiny44a',
    'attiny441',
    'attiny45',
    'attiny461',
    'attiny461a',
    'attiny48',
    'attiny828',
    'attiny84',
    'attiny84a',
    'attiny841',
    'attiny85',
    'attiny861',
    'attiny861a',
    'attiny87',
    'attiny88',
    'avr3',
    'atmega603',
    'at43usb355',
    'avr31',
    'atmega103',
    'at43usb320',
    'avr35',
    'at90usb82',
    'at90usb162',
    'ata5505',
    'ata6617c',
    'ata664251',
    'atmega8u2',
    'atmega16u2',
    'atmega32u2',
    'attiny167',
    'attiny1634',
    'at76c711',
    'avr4',
    'ata6285',
    'ata6286',
    'ata6612c',
    'atmega48',
    'atmega48a',
    'atmega48pa',
    'atmega48p',
    'atmega8',
    'atmega8a',
    'atmega8515',
    'atmega8535',
    'atmega88',
    'atmega88a',
    'atmega88p',
    'atmega88pa',
    'atmega8hva',
    'at90pwm1',
    'at90pwm2',
    'at90pwm2b',
    'at90pwm3',
    'at90pwm3b',
    'at90pwm81',
    'at90can32',
    'avr5',
    'at90can64',
    'at90pwm161',
    'at90pwm216',
    'at90pwm316',
    'at90scr100',
    'at90usb646',
    'at90usb647',
    'at94k',
    'atmega16',
    'ata5790',
    'ata5702m322',
    'ata5782',
    'ata6613c',
    'ata6614q',
    'ata5790n',
    'ata5795',
    'ata5831',
    'atmega161',
    'atmega162',
    'atmega163',
    'atmega164a',
    'atmega164p',
    'atmega164pa',
    'atmega165',
    'atmega165a',
    'atmega165p',
    'atmega165pa',
    'atmega168',
    'atmega168a',
    'atmega168p',
    'atmega168pa',
    'atmega169',
    'atmega169a',
    'atmega169p',
    'atmega169pa',
    'atmega16a',
    'atmega16hva',
    'atmega16hva2',
    'atmega16hvb',
    'atmega16hvbrevb',
    'atmega16m1',
    'atmega16u4',
    'atmega32',
    'atmega32a',
    'atmega323',
    'atmega324a',
    'atmega324p',
    'atmega324pa',
    'atmega325',
    'atmega325a',
    'atmega325p',
    'atmega325pa',
    'atmega3250',
    'atmega3250a',
    'atmega3250p',
    'atmega3250pa',
    'atmega328',
    'atmega328p',
    'atmega329',
    'atmega329a',
    'atmega329p',
    'atmega329pa',
    'atmega3290',
    'atmega3290a',
    'atmega3290p',
    'atmega3290pa',
    'atmega32c1',
    'atmega32hvb',
    'atmega32hvbrevb',
    'atmega32m1',
    'atmega32u4',
    'atmega32u6',
    'atmega406',
    'atmega64rfr2',
    'atmega644rfr2',
    'atmega64',
    'atmega64a',
    'atmega640',
    'atmega644',
    'atmega644a',
    'atmega644p',
    'atmega644pa',
    'atmega645',
    'atmega645a',
    'atmega645p',
    'atmega6450',
    'atmega6450a',
    'atmega6450p',
    'atmega649',
    'atmega649a',
    'atmega6490',
    'atmega6490a',
    'atmega6490p',
    'atmega649p',
    'atmega64c1',
    'atmega64hve',
    'atmega64hve2',
    'atmega64m1',
    'm3000',
    'avr51',
    'at90can128',
    'at90usb1286',
    'at90usb1287',
    'atmega128',
    'atmega128a',
    'atmega1280',
    'atmega1281',
    'atmega1284',
    'atmega1284p',
    'atmega128rfr2',
    'atmega1284rfr2',
    'avr6',
    'atmega2560',
    'atmega2561',
    'atmega256rfr2',
    'atmega2564rfr2',
    'avrxmega2',
    'atxmega16a4',
    'atxmega16a4u',
    'atxmega16c4',
    'atxmega16d4',
    'atxmega32a4',
    'atxmega32a4u',
    'atxmega32c3',
    'atxmega32c4',
    'atxmega32d3',
    'atxmega32d4',
    'atxmega8e5',
    'atxmega16e5',
    'atxmega32e5',
    'avrxmega4',
    'atxmega64a3',
    'atxmega64a3u',
    'atxmega64a4u',
    'atxmega64b1',
    'atxmega64b3',
    'atxmega64c3',
    'atxmega64d3',
    'atxmega64d4',
    'avrxmega5',
    'atxmega64a1',
    'atxmega64a1u',
    'avrxmega6',
    'atxmega128a3',
    'atxmega128a3u',
    'atxmega128b1',
    'atxmega128b3',
    'atxmega128c3',
    'atxmega128d3',
    'atxmega128d4',
    'atxmega192a3',
    'atxmega192a3u',
    'atxmega192c3',
    'atxmega192d3',
    'atxmega256a3',
    'atxmega256a3u',
    'atxmega256a3b',
    'atxmega256a3bu',
    'atxmega256c3',
    'atxmega256d3',
    'atxmega384c3',
    'atxmega384d3',
    'atxmega128a1',
    'avrxmega7',
    'atxmega128a1u',
    'atxmega128a4u',
    'avrtiny10',
    'attiny4',
    'attiny5',
    'attiny9',
    'attiny20',
    'attiny40',
]

programmer_list = [
    'arduino',
    'avr910',
    'avrftdi',
    'buspirate',
    'buspirate_bb',
    'butterfly',
    'butterfly_mk',
    'dragon_dw',
    'dragon_hvsp',
    'dragon_isp',
    'dragon_jtag',
    'dragon_pdi',
    'dragon_pp',
    'ftdi_syncbb',
    'jtagmki',
    'jtagmkii',
    'jtagmkii_avr32',
    'jtagmkii_dw',
    'jtagmkii_isp',
    'jtagmkii_pdi',
    'jtagice3',
    'jtagice3_pdi',
    'jtagice3_dw',
    'jtagice3_isp',
    'linuxgpio',
    'par',
    'pickit2',
    'serbb',
    'stk500',
    'stk500generic',
    'stk500v2',
    'stk500hvsp',
    'stk500pp',
    'stk600',
    'stk600hvsp',
    'stk600pp',
    'usbasp',
    'usbtiny',
    'wiring',
]

def avr_gcc(hardware, programmer, baud):

    def cc_once(cfg):
        lib_flags     = ['-l' + lib for lib in cfg.libs]
        include_flags = ['-I' + inc for inc in cfg.includes]
        hardware_flag = [f'-mmcu={hardware}']
        return {
            'compileflags' : (cfg.flags + include_flags + cfg.compileflags + hardware_flag),
            'linkflags'    : (cfg.flags + include_flags + cfg.linkflags + lib_flags + hardware_flag),
        }
    
    def cc_compile(cfg, source):
        path = cfg.targetpath(source) + '.o'
        cfg.run([
            'avr-gcc', 
            *cfg.once['compileflags'], 
            '-c', source,
            '-o', path
        ])
        return path

    def cc_link(cfg, main, objects):
        path_elf = cfg.targetpath(main) + '.elf'
        path_hex = cfg.targetpath(main) + '.hex' 
        asm = list_files(get_src_path(), with_ext='S')
        cfg.run([
            'avr-gcc',
            main,
            *objects,
            *asm,
            *cfg.once['linkflags'],
            '-o', path_elf,
        ])
        cfg.run([
            'avr-objcopy',
            '-O', 'ihex',
            path_elf,
            path_hex,
        ])
        return path_hex

    def cc_run(cfg, exe):

        @cli_config('port')
        def config_port():
            port = quick_cache()
            if name == 'posix':
                tell('Available ports:')
                cfg.run(['ls /dev/cu.*'], shell=True)
            return quick_cache(ask(('Please enter your device port', ''), default=port))

        cfg.run([
            'avrdude',
            '-v',
            '-p', hardware,
            '-c', programmer,
            '-P', config_port(),
            '-b', baud,
            '-D',
            '-U', f'flash:w:{exe}:i',
        ])

    def cc_debug(cfg, exe):
        panic('Debug is not supported for avr_gcc compiler config!')

    return CompilerConfig(
        name         = 'avr_gcc',
        compile      = cc_compile,
        link         = cc_link,
        run          = cc_run,
        debug        = cc_debug,
        once         = cc_once,
        ccsource     = f'avr_gcc(hardware=\'{hardware}\', programmer=\'{programmer}\', baud=\'{baud}\')',
        csource      = MAIN,
        flags        = ['-Wall'],
        debugflags   = ['-g'],
        releaseflags = ['-O'],
    )

@cli_config('avr_gcc')
def config_avr_gcc():
    return avr_gcc(
        ask((
            'Please select your AVR hardware', 
            '`{}` is not a valid AVR hardware selection!',
        ), options=hardware_list),
        ask((
            'Please select your programmer', 
            '`{}` is not a valid programmer',
        ), default='wiring', options=programmer_list),
        ask((
            'Please select your baud rate',
            '',        
        ), default='115200')
    )