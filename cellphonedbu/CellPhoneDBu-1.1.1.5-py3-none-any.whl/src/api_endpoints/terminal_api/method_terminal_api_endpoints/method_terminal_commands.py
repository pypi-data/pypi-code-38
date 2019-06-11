import sys, traceback
import click

from cellphonedb.src.app import cpdb_app
from cellphonedb.src.app.app_logger import app_logger
from cellphonedb.src.core.exceptions.AllCountsFilteredException import AllCountsFilteredException
from cellphonedb.src.core.exceptions.EmptyResultException import EmptyResultException
from cellphonedb.src.core.exceptions.ThresholdValueException import ThresholdValueException
from cellphonedb.src.exceptions.ReadFileException import ReadFileException
from cellphonedb.src.exceptions.ParseCountsException import ParseCountsException
from cellphonedb.src.exceptions.ParseMetaException import ParseMetaException
from cellphonedb.src.local_launchers.local_method_launcher import LocalMethodLauncher


@click.command()
@click.argument('meta-filename')
@click.argument('counts-filename')
@click.option('--project-name', default='', help='Name of the project. It creates a subfolder in output folder')
@click.option('--log2-transform', default=True, help='log2 transformed all data in counts')
@click.option('--result-precision', default='3', help='Number of decimal digits in results [3]')
@click.option('--output-path', default='',
              help='Directory where the results will be allocated (the directory must exist) [out]')
@click.option('--winsorized-result-name', default='winsorized_count.txt', help='Winsorized result namefile [winsorized_count.txt]')
@click.option('--debug-seed', default='-1', help='Debug random seed 0 for disable it. >=0 to set it [-1]')
@click.option('--threads', default=4, help='Max of threads to process the data [4]')
@click.option('--verbose/--quiet', default=True, help='Print or hide cellphonedb logs [verbose]')
def winsorizer(meta_filename: str,
               counts_filename: str,
               project_name: str,
               log2_transform: bool,
               result_precision: int,
               output_path: str,
               winsorized_result_name: str,
               debug_seed: int,
               threads: int,
               verbose: bool,
               ) -> None:
    try:
        LocalMethodLauncher(cpdb_app.create_app(verbose)). \
            cpdb_statistical_analysis_local_method_launcher(meta_filename,
                                                            counts_filename,
                                                            project_name,
                                                            output_path,
                                                            winsorized_result_name,
                                                            debug_seed,
                                                            threads,
                                                            result_precision,
                                                            log2_transform
                                                            )
    except (ReadFileException, ParseMetaException, ParseCountsException, ThresholdValueException,
            AllCountsFilteredException) as e:
        app_logger.error(str(e) +
                         (':' if (hasattr(e, 'description') and e.description) or (
                                 hasattr(e, 'hint') and e.hint) else '') +
                         (' {}.'.format(e.description) if hasattr(e, 'description') and e.description else '') +
                         (' {}.'.format(e.hint) if hasattr(e, 'hint') and e.hint else '')
                         )

    except EmptyResultException as e:
        app_logger.warning(str(e) +
                           (':' if (hasattr(e, 'description') and e.description) or (
                                   hasattr(e, 'hint') and e.hint) else '') +
                           (' {}.'.format(e.description) if hasattr(e, 'description') and e.description else '') +
                           (' {}.'.format(e.hint) if hasattr(e, 'hint') and e.hint else '')
                           )
    except:
        app_logger.error('Unexpected error')
        if (verbose):
            traceback.print_exc(file=sys.stdout)
