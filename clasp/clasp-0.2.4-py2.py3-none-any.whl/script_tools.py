# Copyright (c) 2018 Stephen Wasilewski
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================

"""library of functions helpful for cli script development and parallel
computing particulary w/ subprocess calls."""

from __future__ import print_function
from __future__ import division
from builtins import map
from builtins import zip
from builtins import str
from builtins import range
from past.utils import old_div
import sys
import shlex
import subprocess
import inspect
import tempfile
import os
import re
import math
import datetime
from clasp import click
import ipyparallel as parallel


def try_mkdir(s):
    '''exception free mkdir'''
    try:
        os.mkdir(s)
    except Exception:
        pass


def arange(start, stop=None, step=1):
    '''like numpy.arange for integers'''
    if stop is None:
        stop = start
        start = 0
    n = int(math.ceil(old_div((stop - start)*1.,step)))
    return [start + step*i for i in range(n)]


def rm_dup(seq):
    """removes duplicates from list while preserving order"""
    mark = set()
    mark_add = mark.add
    return [x for x in seq if not (x in mark or mark_add(x))]


def warn_match(kwargs, sargs):
    for i in sargs:
        if i not in kwargs:
            click.echo('WARNING: {} not set'.format(i), err=True)


def kwarg_match(func, kwargs, debug=False):
    """filters dict for keys used by func"""
    sargs = inspect.getargspec(func).args
    argsc = {i: kwargs[i] for i in sargs if i in kwargs}
    if debug:
        warn_match(kwargs, sargs)
    return argsc


def arg_match(func, kwargs, *args):
    """filters dict for positional arguments used by func"""
    sargs = inspect.getargspec(func).args[len(args):]
    argsc = list(args) + [kwargs[i] if i in kwargs else None for i in sargs]
    return argsc


def kwarg_arg(func, kwargs, skip=None):
    """returns ordered list of optional arg values"""
    spec = inspect.getargspec(func)
    if skip is not None:
        oargs = spec.args[skip:]
    else:
        oargs = spec.args[-len(spec.defaults):]
    largs = []
    for oarg, default in zip(oargs, spec.defaults):
        try:
            largs.append(kwargs[oarg])
        except Exception:
            largs.append(default)
    return largs


def crossref(l1, l2):
    '''return all possible pairs of 2 lists'''
    n = len(l1) * len(l2)
    out = [[] for i in range(n)]
    for i, l in enumerate(l1):
        for j, m in enumerate(l2):
            out[i*len(l2)+j] += [l, m]
    return [flat_list(i) for i in out]


def crossref_all(l, followers=[]):
    '''return all possible combos of list of lists'''
    la = []
    followed = [i[0] for i in followers]
    follows = [i[1] for i in followers]
    leaders = [i for i in range(len(l)) if i not in follows]
    for i in leaders:
        if i == 0:
            if i in followed:
                k = follows[followed.index(i)]
                try:
                    la = [[lb, l[k][j]] for j,lb in enumerate(l[i])]
                except:
                    click.echo('length of follower must match leader', err=True)
                    raise click.Abort()
            else:
                la = l[i]
        else:
            if i in followed:
                lb = crossref(la, list(range(len(l[i]))))
                k = follows[followed.index(i)]
                try:
                    la = [j[:-1] + [l[i][j[-1]], l[k][j[-1]]] for j in lb]
                except IndexError:
                    click.echo('length of follower must match leader', err=True)
                    raise click.Abort()
            else:
                la = crossref(la, l[i])
    return list(zip(*la))


def subpipe(commands):
    '''
    parses special syntax in pipe expressions

    | $(some command) executes to a temporary file whose path is inserted in
    | the command.
    | $((expression)) evaluates a arithmetic expression in place +-*/()
    '''
    temps = []
    for i, command in enumerate(commands):
        if re.match('.*\$\(.+\).*', command):
            subs = re.findall('\$\(.+\)', command)
            for sub in subs:
                if "$((" in sub:
                    pt = sub[:]
                    while "$((" in pt:
                        si = pt.rfind("$((")
                        op = 2
                        sj = si+3
                        for s in pt[sj:]:
                            if op == 0:
                                break
                            if s == "(":
                                op += 1
                            if s == ")":
                                op -= 1
                            sj += 1
                        try:
                            exp = pt[si+1:sj]
                            pt = pt[:si] + str(eval(exp, {}, {})) + pt[sj:]
                        except Exception:
                            click.echo("bad expression: {}".format(exp))
                            raise click.Abort
                else:
                    f, pt = tempfile.mkstemp(dir="./", prefix='clasp_tmp')
                    temps.append(pt)
                    pipeline([sub.strip('$()')], outfile=pt)
                commands[i] = command.replace(sub, pt)
    return temps, commands


def pipeline(commands, outfile=None, inp=None, close=False, cwd=None,
             writemode='w', forceinpfile=False):
    """
    executes pipeline of shell commands (given as list of strings)

    Parameters
    ----------
    commands: list
        list of commands to execute in order
    outfile: writeable file object
        optional destination for stdout
    inp: str or filebuffer
        string to feed to stdin at start of pipeline
    close: bool
        if true closes file object before returning

    Returns
    -------
    out: str
        returns stdout of pipeline (will be None if outfile is given)
    """
    temps, commands = subpipe(commands)
    pops = [0]*len(commands)
    if outfile is not None and not hasattr(outfile, 'read'):
        if cwd is not None:
            outfile = open(cwd + "/" + outfile, writemode)
        else:
            outfile = open(outfile, writemode)
    for i in range(len(commands)):
        if i == 0:
            if hasattr(inp, 'read'):
                strin = False
                stdin = inp
            elif forceinpfile and inp is not None:
                strin = False
                stdin = open(inp, 'r')
            elif inp is not None:
                strin = True
                stdin = subprocess.PIPE
            else:
                strin = True
                stdin = None
        else:
            stdin = pops[i-1].stdout
        if i == len(commands) - 1 and outfile is not None:
            stdout = outfile
        else:
            stdout = subprocess.PIPE
        try:
            pops[i] = subprocess.Popen(shlex.split(commands[i]),
                                       stdin=stdin, stdout=stdout, cwd=cwd)
        except OSError:
            message = "invalid command / no such file: {}".format(commands[i])
            raise OSError(2, message)
    try:
        inp = inp.encode(sys.stdin.encoding)
    except Exception:
        pass
    if len(commands) == 1 and strin:
        out = pops[0].communicate(inp)[0]
    else:
        if inp is not None and strin:
            pops[0].stdin.write(inp)
            pops[0].stdin.close()
        out = pops[-1].communicate()[0]
    try:
        out = out.decode(sys.stdout.encoding)
    except Exception:
        pass
    if close:
        outfile.close()
    for temp in temps:
        os.remove(temp)
    return out


def flat_list(l):
    """flattens any depth list"""
    a = []
    try:
        if type(l) == list:
            for i in l:
                a += flat_list(i)
        else:
            a.append(l)
    except Exception:
        a.append(l)
    return a


def cluster_call(func, args, profile=None, kwargs=None, timeout=.1, cwd=None,
                 debug=False):
    """
    execute func on ipcluster if available return output

    Parameters
    ----------
    func: python function
        function to execute
    outfile: list of args
        each item is mapped to function
    profile: str
        name of ipcluster profile to execute on

    Returns
    -------
    out: list
        returns stdout of each function call
    """

    def dirfunc(*args):
        """set directory for func with file dependencies"""
        if cwd is not None:
            os.chdir(cwd)
        return func(*args)

    args2 = (dirfunc,) + args
    if kwargs is not None:
        largs = kwarg_arg(func, kwargs, len(args))
        args2 += tuple([i]*len(args[0]) for i in largs)
    message = "start ipcluster for faster calculations ("\
              "'ru_start cluster')".format(profile)
    try:
        pidf = '~/.ipython/profile_{}/pid/ipcluster.pid'.format(profile)
        if os.path.isfile(os.path.expanduser(pidf)):
            clients = parallel.Client(profile=profile, timeout=timeout)
            dview = clients[:]
            dview.push(dict(func=func, dirfunc=dirfunc, cwd=cwd))
            clients.block = True  # use synchronous computations
            view = clients.load_balanced_view()
            output = view.map(*args2)
        else:
            print(message, file=sys.stderr)
            output = list(map(*args2))
    except Exception as ex:
        if debug:
            print(ex, file=sys.stderr)
        print(message, file=sys.stderr)
        output = list(map(*args2))
    return output


def cluster_command(com, cwd, stdin=None, stdout=None, shell=True):
    import subprocess
    if stdin:
        d = open(cwd + stdin, 'r')
    else:
        d = None
    if stdout:
        g = open(cwd + stdout, 'w')
        h = subprocess.PIPE
    else:
        g = subprocess.PIPE
        h = subprocess.PIPE
    f = subprocess.Popen(com, stdin=d, stdout=g, stderr=h,
                         cwd=cwd, shell=shell).communicate()
    return f


def get_results(ar, stdout, coms, sh, i):
    """get results from asyncronous results when ready use in while pending"""
    if stdout is not None:
        f = open(stdout, 'a')
    else:
        f = sys.stdout
    try:
        for r in ar.get():
            click.echo("{}:".format(coms[i].strip()), err=True)
            click.echo(r[1], err=True)
            print(r[0].strip(), file=f)
            g = open(sh.replace(".sh", "_completed.txt"), 'a')
            now = datetime.datetime.now()
            ts = "Completed @ {:%b %d, %Y, %H:%M:%S}: {}".format(now, coms[i])
            print(ts, file=g)
            g.close()
            i += 1
    except Exception:
        g = open(sh.replace(".sh", "_error.txt"), 'a')
        print(coms[i], file=g)
        g.close()
        print("####MISSING DATA CHECK ERROR.TXT#### ", file=f, end="")
        print("command: {}".format(coms[i].strip()), file=f)
        i += 1
    if stdout is not None:
        f.close()
    return i


def run_sh(remotes, sh, prof, cwd,
           stdout=None, ordered=False, nodir=False, exclude="NOTRANSFER/"):
    try:
        clients = parallel.Client(profile=prof)
        clients.block = False
    except Exception as inst:
        print(inst.args[0], file=sys.stderr)
    else:
        abspath = os.path.abspath(sh)
        workdir = abspath.rsplit("/", 1)[0] + "/"
        click.echo(workdir, err=True)
        if not nodir:
            cwd = send_working_dir(remotes, workdir, cwd, exclude=exclude)
            click.echo(cwd, err=True)
        else:
            cwd = cwd + "/" + workdir.strip("/").split("/")[-1]
        f = open(sh, 'r')
        coms = [i for i in f.read().strip().split("\n")
                if (i.strip() is not "" and i.strip()[0] != "#")]
        f.close()
        cwds = [cwd]*len(coms)
        view = clients.load_balanced_view()
        output = view.map(cluster_command, coms, cwds,
                          ordered=ordered, chunksize=1)
        i = 0
        if stdout is not None:
            f = open(stdout, 'w')
            f.close()
        pending = output.msg_ids
        g = open(sh.replace(".sh", "_completed.txt"), 'a')
        now = datetime.datetime.now()
        ts = "Run Began @ {:%b %d, %Y, %H:%M:%S}".format(now)
        print(ts, file=g)
        g.close()
        while pending:
            msg_id = pending[0]
            clients.wait(msg_id)
            pending = pending[1:]
            ar = clients.get_result(msg_id)
            i = get_results(ar, stdout, coms, sh, i)


def start_farm(remotes, prof, thr):
    """output shell command for starting farm"""
    rem = ", ".join(['\"{}\":{}'.format(i, thr) for i in remotes])
    click.echo("ipcluster start --profile={} "
               "--SSHEngineSetLauncher.engines='{{{}}}'".format(prof, rem),
               err=True)


def stop_farm(profile):
    msg = "Are you sure you want to shutdown {}?".format(profile)
    if click.confirm(msg, default=True):
        try:
            clients = parallel.Client(profile=profile)
            clients.shutdown(hub=True)
        except Exception as inst:
            print(inst.args[0], file=sys.stderr)


def add_engine(remotes, sh, prof, thr,
               nodir=False, exclude="NOTRANSFER/"):
    """call ipcluster to add additional engines to farm"""
    if not nodir:
        abspath = os.path.abspath(sh)
        workdir = abspath.rsplit("/", 1)[0] + "/"
        print(workdir, file=sys.stdout)
        send_working_dir(remotes, workdir, exclude=exclude)
    for remote in remotes:
        rem = '"{}":{}'.format(remote, thr)
        command = "ipcluster engines --daemonize  --profile={}"\
                  " --SSHEngineSetLauncher.engines={{{}}}".format(prof, rem)
        subprocess.call(command.split())


def remove_engines(remotes):
    """remove remote from ipcluster"""
    for r in remotes:
        try:
            pgrep = ['pgrep', '-f', 'ssh -tt {}'.format(r)]
            pid = subprocess.check_output(pgrep).split()
        except Exception:
            click.echo("no pid found for remote: {}".format(r))
            pass
        else:
            for p in pid:
                subprocess.call(['kill', p])


def send_working_dir(remotes, workdir,
                     cwd="ipcluster", exclude="NOTRANSFER/"):
    """transfer file dependencies to remotes"""
    workf = cwd + "/" + workdir.strip("/").split("/")[-1]
    for remote in remotes:
        scp = "rsync -av --exclude {3} {0} {1}:{2}".format(workdir, remote,
                                                           workf, exclude)
        click.echo(scp, err=True)
        subprocess.call(scp.split())
    return workf


def get_cpu(remotes, stat=None, cwd="ipcluster"):
    """print top usage stats for remotes"""

    def data_line(l):
        """format for usage stats"""
        return "{: <20}{: <8}{: <8}{: <10}{: <10}{}".format(l[0], l[2], l[3],
                                                            l[8], l[9], l[10])

    for remote in remotes:
        try:
            output = subprocess.check_output("ssh -o ConnectTimeout=10 {} "
                                             "'ps aux'".format(remote),
                                             shell=True).strip().split("\n")
        except Exception:
            click.echo("unable to connect to {}".format(remote), err=True)
        else:
            output = [i.split(None, 10) for i in output]
            click.echo("{}:\n".format(remote), err=True)
            li = [j.split("/")[-1] for j in output[0]]
            click.echo(data_line(li), err=True)
            for i in output[1:]:
                if float(i[2]) > 5 and i[0] != "root":
                    li = [j.split("/")[-1][:30] for j in i]
                    click.echo(data_line(li), err=True)
            cpus = sum([float(j[2]) for j in output[1:]])
            print("\nCPU:{}/800\n".format(cpus), file=sys.stderr)
            chk = "ssh -o ConnectTimeout=10 {} 'ls -l {}/{} | cut -c-100'"\
                  "".format(remote, cwd, stat)
            output = subprocess.check_output(chk, shell=True).strip()
            for i in output.split("\n"):
                click.echo(i, err=True)


def check_farm(profile):
    """output number of engines running on farm"""
    try:
        clients = parallel.Client(profile=profile)
        ids = clients.ids
        click.echo(ids, err=True)
    except Exception as inst:
        click.echo(inst.args[0], err=True)


def gather_files(remotes, get, rsync, cwd="ipcluster", nocheck=False):
    """gather files from list of remotes via rsync and ssh"""
    dash = "________________________"
    if not nocheck:
        click.echo("{0}\n\nrsync --dry-run results:\n{0}\n".format(dash),
                   err=True)
        for rem in remotes:
            scp = "rsync -av {3} {0}:{1}/{2} ./ --dry-run".format(rem, cwd,
                                                                  get, rsync)
            subprocess.call(scp.split())
        click.echo("{0}\n{0}\n".format(dash), err=True)
    if nocheck or click.confirm("Proceed with rsync?", default=True):
        for rem in remotes:
            scp = "rsync -av {3} {0}:{1}/{2} ./".format(rem, cwd, get, rsync)
            subprocess.call(scp.split())


def dist_command(remotes, command):
    """run command once on each remote"""
    output = []
    for remote in remotes:
        sshaux = "ssh -o ConnectTimeout=10 {} '{}'".format(remote, command)
        output.append(subprocess.check_output(sshaux, shell=True).strip())
    return output


def get_cpu_log(remotes):
    cpus = []
    for remote in remotes:
        try:
            sshaux = "ssh -o ConnectTimeout=10 {} 'ps aux'".format(remote)
            out = subprocess.check_output(sshaux,
                                          shell=True).strip().split("\n")
        except Exception:
            print("unable to connect to {}".format(remote), file=sys.stderr)
            cpus.append("XXXXX   " + "X"*32)
        else:
            out = [i.split(None, 10) for i in out]
            cpu = sum([float(j[2]) for j in out[1:]])
            bar = min(32, int(round(old_div(cpu,800*32))))
            cpus.append("{: <8}{}{}".format(cpu, "#"*bar, "."*(32-bar)))
    return cpus


def farm_log(remotes, interval, outf="farm_log.txt"):
    """record cpu usage of ssh remotes"""
    import time
    stime = time.time()
    while True:
        cpus = get_cpu_log(remotes)
        f = open(outf, 'a')
        vals = "\t".join(cpus)
        ti = time.strftime("%m/%d/%y-%H:%M:%S")
        f.write("{}\t{}\n".format(ti, vals))
        f.close()
        time.sleep(interval - ((time.time() - stime) % interval))


def read_epw(epw):
    '''read daylight sky data from epw or wea file

    Returns
    -------
    out: tuple
        (month, day, hour, dirnorn, difhoriz, globhoriz, skycover)
    '''
    if hasattr(epw, 'readlines'):
        f = epw
    else:
        f = open(epw, 'r')
    lines = f.readlines()
    f.seek(0)
    hours = [re.split('[ \t,]+', i) for i in lines if re.match("\d.*", i)]
    data = []
    for h in hours:
        if len(h) > 23:
            dp = [h[1], h[2], h[3], h[14], h[15], h[16], h[23]]
            hoff = .5
        else:
            try:
                dp = [h[0], h[1], h[2], h[3], h[4], h[5], h[6]]
            except IndexError:
                dp = [h[0], h[1], h[2], h[3], h[4], "0", "0"]
            hoff = 0
        data.append([int(i.strip()) for i in dp[0:2]] +
                    [float(dp[2]) - hoff] +
                    [float(i.strip()) for i in dp[3:]])
    return data


def isnum(s):
    """test if input can be converted to float"""
    try:
        float(s)
        return True
    except Exception:
        return False


def try_float(s):
    """attempt conversion to float"""
    try:
        a = float(s)
        return a
    except Exception:
        return s


def coerce_data(datastr, i_vals, dataf, coerce=True):
    '''ensure all data points parsed are valid numbers'''
    try:
        if coerce:
            data = [[float(j[i]) for j in datastr if isnum(j[i])]
                    for i in i_vals]
            if len(data[0]) == 0:
                raise ValueError("check if data file {} has xheaders"
                                 "".format(dataf))
        else:
            data = [[try_float(j[i]) for j in datastr] for i in i_vals]
    except ValueError as ex:
        raise ex
    except Exception:
        try:
            err = "list index out of range index: {} in file: {}"\
                  "".format(i, dataf)
        except:
            err = "bad value or no data in file: {}, try --no-coerce"\
                  "".format(dataf)
        raise IndexError(err)
    return data


def get_i(i, d_vals):
    """
    if (x, y) return y if x == i
    if y return y
    """
    ds = []
    for j in d_vals:
        if type(j) == tuple and j[0] == i:
            ds.append(j[1])
        elif type(j) != tuple:
            ds.append(j)
    return ds


def read_data_file(dataf, header, xheader, comment, delim):
    delim = '[{}]+'.format(delim)
    if comment != "#":
        comment = "^[{}].*".format(comment)
    elif not header and coerce:
        comment = "^[^\-\d\w].*"
    else:
        comment = "^[{}].*".format(comment)
    f = open(dataf, 'r')
    dl = [i.strip() for i in re.split('[\n\r]+', f.read().strip())]
    if xheader:
        dl = [re.split(delim, i.strip(), 1)[1] for i in dl]
    dl = [i for i in dl if not bool(re.match(comment, i))]
    if len(dl) == 0:
        click.echo("File: {} has no data".format(dataf), err=True)
        raise click.Abort()
    datastr = [[j.strip() for j in re.split(delim, i.strip())] for i in dl]
    f.close()
    return datastr


def read_data(dataf, x_vals=[0], y_vals=[-1], rows=False, header=False,
              weax=None, reverse=False, autox=None, comment="#", xheader=False,
              delim="\t, ", coerce=True, weatherfile=False, drange=None):
    """read generic csv/tsv data file

    Parameters
    ----------
    dataf: str
        file to read data from
    x_vals: list of ints
        column (or row with rows=True) indices for x values
    y_vals: list of ints
        column (or row with rows=True) indices for y values
    rows: Boolean
        if True read data in rows
    header: Boolean
        return first row (or column with rows=True) as series labels
    weax: 2 item list of ints
        idx for month and day to use day number as x_vals, if given ignores
        x_val
    reverse: Boolean
        reverse order of data (use with autox)
    autox: Boolean
        assigns integers (starting at 0) as x_vals
    comment: str
        comment line signifiers (inserted in regex ^[comment].*)
    delim: str
        delimeters for parsing data (inserted in regex [delim]+)
    coerce: Boolean
        raise exception if all values are are not numbers
    weatherfile: str of file path
        handles wea and epw file formates returning daylight parameters
    drange: list of ints
        limit series output to given indices.

    Returns
    -------
    datax: list
        list of x_vals for each y_val (pads with last item if necessary)
        if there are more x_vals than y_vals does not return excess datax
    datay: list
        list for each y_val
    head: list
        if header=True list of labels for each y_val else []
    """
    if weatherfile:
        datastr = [[str(i) for i in j] for j in read_epw(dataf)]
        head = ['month', 'day', 'hour', 'direct normal', 'diffuse horizontal',
                'global horizontal', 'sky cover']
        head = [head[i] for i in y_vals]
    else:
        datastr = read_data_file(dataf, header, xheader, comment, delim)
        if header:
            head = [datastr[0][i] for i in y_vals]
            datastr = datastr[1:]
        else:
            head = []
        if reverse:
            datastr.reverse()
        if rows:
            datastr = list(map(list, list(zip(*datastr))))
    if drange is not None:
        datastr = [v for i, v in enumerate(datastr) if i in drange]
    if len(y_vals) > 0:
        datay = coerce_data(datastr, y_vals, dataf, coerce)
    else:
        datay = [[]]
    if autox is not None:
        datax = []
        for i in datay:
            try:
                inc = (autox[1]-autox[0])/float(len(i)-1)
                datax.append([j*inc+autox[0] for j in range(len(i))])
            except ZeroDivisionError:
                datax.append([autox[0]])
    elif weax is not None:
        daycount = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        datax = [[float(j[i]) for i in weax]
                 for j in datastr if isnum(j[weax[0]])]
        datax = [[daycount[int(i[0])-1] + i[1] for i in datax]]
    else:
        if len(x_vals) > 0:
            datax = coerce_data(datastr, x_vals, dataf, coerce)
        else:
            datax = [[]]
    while len(datax) < len(datay) and len(datax) > 0:
        datax += [datax[-1]]
    if len(datax) > len(datay):
        datax = datax[:len(datay)]
    return datax, datay, head


def read_all_data(datafs, x_vals=[], y_vals=[], **kwargs):
    """
    read multiple data files and pair x and y data call read_data

    Parameters
    ----------
    datafs: list of str
        files to read data from
    x_vals: list of ints or tuple int pairs
        (fileidx, colidx) or colidx to read from each file
    y_vals: list of ints or tuple int pairs
        (fileidx, colidx) or colidx to read from each file
    kwargs:
        optional arguments for read_data

    Returns
    -------
    datax: list
        list of x_vals for each y_val (pads with last item if necessary)
    datay: list
        list for each y_val
    head: list
        if header=True list of labels for each y_val else []
    """
    xds = []
    yds = []
    labels = []
    try:
        if kwargs['autox']:
            x_vals = y_vals
    except Exception:
        pass
    for x in x_vals:
        if type(x) == tuple:
            xd, _, _ = read_data(datafs[x[0]], [x[1]], [-1], **kwargs)
            xds += xd
        else:
            for d in datafs:
                xd, _, _ = read_data(d, [x], [-1], **kwargs)
                xds += xd
    for y in y_vals:
        if type(y) == tuple:
            _, yd, label = read_data(datafs[y[0]], [], [y[1]], **kwargs)
            yds += yd
            labels += label
        else:
            for d in datafs:
                _, yd, label = read_data(d, [], [y], **kwargs)
                yds += yd
                labels += label
    while len(xds) < len(yds) and len(xds) > 0:
        xds += [xds[-1]]
    return xds, yds, labels
