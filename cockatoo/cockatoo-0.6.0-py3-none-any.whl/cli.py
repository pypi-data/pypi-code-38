import os
import click
import csv
import re
import urllib2
import json
import cockatoo
import logging
import numpy as np

class WeightsParamType(click.ParamType):
    name = 'weights'

    def convert(self, value, param, ctx):
        if value is None or len(value) == 0:
            return [1.0,1.0]

        try:
            weights = [float(w) for w in str(value).split(',')]
            if len(weights) != 2:
                self.fail('%s must be of the form w1,w2' % value, param, ctx)
            if sum(weights) <= 0:
                self.fail('%s sum must be >=0' % value, param, ctx)
            return weights
        except ValueError:
            self.fail('%s is not a valid float' % value, param, ctx)

WEIGHTS_PARAM = WeightsParamType()

@click.group()
@click.option('--verbose', '-v', is_flag=True, default=False, help='Turn on verbose logging')
@click.pass_context
def cli(ctx, verbose):
    ctx.obj['VERBOSE'] = verbose
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

@cli.command()
@click.pass_context
def version(ctx):
    """Print cockatoo version"""
    click.echo('cockatoo v{}'.format(cockatoo.__version__))

@cli.command()
@click.option('--name', '-n', default='screen', help='Name of the screen')
@click.option('--csvin', '-i', required=True, type=click.File(mode='r'), help='Path to input csv file')
@click.option('--output', '-o', required=True, type=click.File(mode='w'), help='Path to output file')
@click.option('--summary', '-s', required=False, type=click.Path(), help='Path to compound summary data')
@click.pass_context
def convert(ctx, name, csvin, output, summary):
    """Convert CSV screen to JSON format"""
    screen = cockatoo.screen.Screen(name)
    reader = csv.reader(csvin)
    for row in reader:
        # Skip comments
        if re.search(r'^#', row[0]): continue
        cocktail = cockatoo.screen._parse_cocktail_csv(row)
        if cocktail is not None:
            screen.add_cocktail(cocktail)

    if summary:
        screen._set_summary_stats(summary)

    output.write(screen.json())

    if ctx.obj['VERBOSE']:
        click.echo("Screen stats:")
        screen.print_stats()
        click.echo("Done converting screen.")

@cli.command()
@click.option('--cocktail1', '-1', required=True, type=click.Path(), help='Path to cocktail1 in JSON format')
@click.option('--cocktail2', '-2', required=True, type=click.Path(), help='Path to cocktail2 in JSON format')
@click.option('--weights', '-w', type=WEIGHTS_PARAM, help='weights=1,1')
@click.pass_context
def cdist(ctx, cocktail1, cocktail2, weights):
    """Compute the distance between 2 cocktails"""
    ck1 = cockatoo.screen.parse_cocktail(cocktail1)
    ck2 = cockatoo.screen.parse_cocktail(cocktail2)

    click.echo("Computing distance between {} and {}...".format(ck1.name, ck2.name))
    score = cockatoo.metric.distance(ck1, ck2, weights)
    click.echo("Distance: {}".format(score))

@cli.command()
@click.option('--screen1', '-1', required=True, type=click.Path(), help='Path to screen1 in JSON format')
@click.option('--screen2', '-2', required=True, type=click.Path(), help='Path to screen2 in JSON format')
@click.option('--weights', '-w', type=WEIGHTS_PARAM, help='weights=1,1')
@click.pass_context
def sdist(ctx, screen1, screen2, weights):
    """Compute the distance between 2 screens"""
    s1 = cockatoo.screen.load(screen1)
    s2 = cockatoo.screen.load(screen2)

    click.echo("Computing distance between {} and {}...".format(s1.name, s2.name))
    score = cockatoo.screen.distance(s1, s2, weights)
    click.echo("Distance: {}".format(score))

@cli.command()
@click.option('--screen', '-s', required=True, type=click.Path(), help='Path to screen in JSON format')
@click.option('--weights', '-w', type=WEIGHTS_PARAM, help='weights=1,1')
@click.pass_context
def isim(ctx, screen, weights):
    """Compute the internal similarity score for a screen"""
    s = cockatoo.screen.load(screen)

    click.echo("Computing internal similarity for {}...".format(s.name))
    score = cockatoo.screen.internal_similarity(s, weights)
    click.echo("Internal similarity score: {}".format(score))

@cli.command()
@click.option('--screen', '-s', default=None, type=click.Path(), help='Path to screen in JSON format')
@click.option('--xid', '-i', default=0, type=int, help='Xtuition screen id to fetch using Api')
@click.option('--pdist', '-p', is_flag=True, default=False, help='output pairwise distances')
@click.option('--dendrogram', '-d', is_flag=True, default=False, help='output dendrogram')
@click.option('--newick', '-n', is_flag=True, default=False, help='output dendrogram in newick format')
@click.option('--basename', '-b', default='cockatoo-hclust', help='basename for output files')
@click.option('--cutoff', '-c', default=0.7, type=float, help='percent of max cophenetic distance to use as cutoff')
@click.option('--weights', '-w', type=WEIGHTS_PARAM, help='weights=1,1')
@click.option('--dm', '-x', default=None, type=click.Path(), help='Path to pre-computed distance matrix')
@click.option('--stats', '-l', is_flag=True, default=False, help='Output cluster statistics')
@click.pass_context
def hclust(ctx, screen, xid, pdist, dendrogram, newick, basename, cutoff, weights, dm, stats):
    """Perform hierarchical clustering on a screen"""
    try:
        import cockatoo.hclust
    except Exception, e:
        click.echo('Fatal Error loading hclust. Please install required packages: {}'.format(e))
        return 1
        
    if xid == 0 and screen is None:
        click.echo('Must provide either a screen or xid')
        return 1

    if xid > 0:
        req = urllib2.Request('http://xtuition.org/api/screen/{}/cockatoo'.format(int(xid)))
        if 'XTUITION_TOKEN' not in os.environ:
            click.echo('Please set XTUITION_TOKEN environment variable')
            return 1
        req.add_header('Authorization', 'Bearer {}'.format(os.environ['XTUITION_TOKEN']))
        resp = urllib2.urlopen(req)
        s = cockatoo.screen.loads(resp.read())
    else:
        s = cockatoo.screen.load(screen)

    distanceMatrix = None
    if dm is not None:
        with open(dm, 'r') as fin:
            distanceMatrix = np.load(fin)

    cockatoo.hclust.cluster(s, weights, cutoff, basename, distanceMatrix, pdist, dendrogram, newick, stats)

def main():
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.CRITICAL
    )

    cli(obj={})

if __name__ == '__main__':
    main()
