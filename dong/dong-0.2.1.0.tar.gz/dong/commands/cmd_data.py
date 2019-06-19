import click
import dong
import dong.httpclient as httpclient
#import requests

@click.command()
def command():
   """[Not released yet] storage integration"""
   click.echo('command \"data\" Not released in pre-α')
   return None

# def _copy(src, dst):
#    click.echo('copy %s to folder %s ...' % (src, dst))
#    files = {'file': open(src, 'rb')}
#    r = httpclient.post('api/v1/copy/', json = {'dst_name': dst}, files = files)
#    if r.status_code == 200:
#       click.echo('data [%s] URL lg://%s' % (src,dst))
#    else:
#       print('ERROR,[internet connection, sever error, ...]')
#       return None

# @click.group()
# def command():
#    """storage integration"""
#    pass

# @command.command(help="Copy local file to bucket")
# @click.argument('src', nargs=-1, required = True)
# @click.argument('dst', nargs=1, required = True)
# def cp(src, dst):
#    _copy(src, dst)

# # @command.command(help="Make a bucket")
# # @click.argument('dst', nargs=1, required = True)
# # def mb(dst):
# #    click.echo("mb")

# @command.command(help="Remove file on cloud")
# @click.argument('dst', nargs=1, required = True)
# def rm(dst):
#    click.echo("remove")

# @command.command(help="List dst/file on cloud")
# def ls():
#    click.echo("list")#顯示bucket的list
#  No newline at end of file
