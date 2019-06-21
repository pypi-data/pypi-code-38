"""Gets statistics on the average face size in a video database.
"""
import logging
import click
import numpy as np
from os.path import expanduser
from bob.extension.scripts.click_helper import (
    verbosity_option, ConfigCommand, ResourceOption)
from bob.ip.facedetect import (
    bounding_box_from_annotation, expected_eye_positions, BoundingBox)

logger = logging.getLogger(__name__)
BF = 'Bona Fide'
PA = 'Presentation Attack'


@click.command(entry_point_group='bob.bio.config', cls=ConfigCommand)
@click.option('--database', '-d', required=True, cls=ResourceOption,
              entry_point_group='bob.pad.database')
@click.option('-o', '--output', default='face_sizes.png')
@click.option('--database-directories-file', cls=ResourceOption,
              default=expanduser('~/.bob_bio_databases.txt'))
@verbosity_option(cls=ResourceOption)
def statistics(database, output, database_directories_file, **kwargs):
    """Statistics on face size in video databases.

    \b
    Parameters
    ----------
    database : :any:`bob.pad.database`
        The database that you want to annotate. Can be a ``bob.pad.database``
        entry point or a path to a Python file which contains a variable
        named `database`.
    output : str
        Path to the saved figure.
    database_directories_file : str
        Path to a custom ``~/.bob_bio_databases.txt`` file.
    verbose : int, optional
        Increases verbosity (see help for --verbose).

    \b
    [CONFIG]...            Configuration files. It is possible to pass one or
                           several Python files (or names of ``bob.bio.config``
                           entry points) which contain the parameters listed
                           above as Python variables. The options through the
                           command-line (see below) will override the values of
                           configuration files.
    """
    logger.debug('database: %s', database)
    logger.debug('output: %s', output)
    logger.debug('database_directories_file: %s', database_directories_file)
    logger.debug('kwargs: %s', kwargs)

    # Some databases need their original_directory to be replaced
    database.replace_directories(database_directories_file)

    biofiles = database.objects(groups=None, protocol=database.protocol)
    biofiles = sorted(biofiles)

    logger.info("Gathering face size statistics of %d samples", len(biofiles))

    face_sizes_dict = {BF: [], PA: []}
    for i, biofile in enumerate(biofiles):
        for annot in database.annotations(biofile).values():
            # get the bounding box
            for source in ('direct', 'eyes', None):
                try:
                    bbx = bounding_box_from_annotation(source=source, **annot)
                    break
                except Exception:
                    if source is None:
                        raise
                    else:
                        pass
            # record face size
            if biofile.attack_type is None:
                face_sizes_dict[BF].append(bbx.size)
            else:
                face_sizes_dict[PA].append(bbx.size)

    if output:
        import matplotlib.pyplot as plt
        # from matplotlib.backends.backend_pdf import PdfPages
        # pp = PdfPages(output)

    for attack_type, face_sizes in face_sizes_dict.items():
        click.echo(attack_type)
        face_sizes = np.array(face_sizes)
        # get statistics on the face sizes
        for name, array in (
            ('Height', face_sizes[:, 0]),
            ('Width', face_sizes[:, 1]),
        ):
            click.echo('min: {}, mean: {}, max: {}, std: {:.1f} for {}'.format(
                array.min(), int(array.mean()), array.max(), array.std(),
                name))
        # print the average eye distance assuming bounding boxes are from
        # bob.ip.facedetect or the annotations had eye locations in them
        bbx = BoundingBox((0, 0), face_sizes.mean(axis=0))
        annot = expected_eye_positions(bbx)
        eye_distance = np.linalg.norm(
            np.array(annot['reye']) - np.array(annot['leye']))
        click.echo('Average eye locations: {}'.format(annot))
        click.echo('Average eye distance: {}'.format(int(eye_distance)))

        if not output:
            continue

        # plot the face sizes

        # plt.hist2d(face_sizes[:, 1], face_sizes[:, 0], bins=500)
        # plt.xlabel('Width')
        # plt.ylabel('Height')
        # plt.grid()

        # from matplotlib import cm
        # from mpl_toolkits.mplot3d import Axes3D
        # Z, xedges, yedges, _ = plt.hist2d(
        #     face_sizes[:, 1], face_sizes[:, 0], bins=500, normed=True)
        # xcenters = (xedges[:-1] + xedges[1:]) / 2
        # ycenters = (yedges[:-1] + yedges[1:]) / 2
        # X, Y = np.meshgrid(xcenters, ycenters)
        # fig = plt.figure()
        # ax = Axes3D(fig)
        # ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.viridis)

        plt.hist(face_sizes[:, 1], density=True,
                 bins='auto', label=attack_type,
                 alpha=0.5)
    if output:
        plt.xlabel('Width of faces')
        plt.ylabel('Probability Density')

        plt.tight_layout()
        plt.legend()
        plt.savefig(output)
        # pp.savefig(plt.gcf())
