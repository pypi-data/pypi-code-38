

import shutil
from graffunc import graffunc
from rofetta import to_lp, autoconv
from rofetta.utils import format_from_filename, basename_from_filename


# NB: graffunc do not help ; its next version should benefit from this experiment
grfc = graffunc({
    ('slf',): {
        ('cxt',): lambda slf: {'cxt': autoconv.convert_slf_to_cxt(slf)}
    },
    ('cxt',): {
        ('lp',): lambda cxt: {'lp': to_lp.convert_cxt_to_lp(cxt)},
        ('slf',): lambda cxt: {'slf': autoconv.convert_cxt_to_slf(cxt)},
    },
    ('txt',): {
        ('lp',): lambda txt: {'lp': to_lp.convert_txt_to_lp(txt)}
    },
    ('csv',): {
        ('lp',): lambda csv: {'lp': to_lp.convert_csv_to_lp(csv)}
    },
})


def convert(fin:str, fout:str):
    input_format = format_from_filename(fin)
    output_format = format_from_filename(fout)

    res = grfc.convert(sources={input_format: fin}, targets={output_format})
    shutil.move(res[output_format], fout)
