def add_pipeline_tool(parser):
    pipeline_parser = parser.add_parser(
        'pipeline',
        prog='lib5c pipeline',
        help='run entire pipeline',
    )
    pipeline_parser.add_argument(
        '-R', '--remote_scheduler',
        action='store_true',
        help='''Use a remote luigi scheduler instead of the local scheduler.''')
    pipeline_parser.add_argument(
        '-t', '--task_class',
        type=str,
        help='''Custom Task class defining the pipeline, in the form
        'my_module.MyTask' where my_module is available on the PYTHONPATH.''')
    pipeline_parser.add_argument(
        '-d', '--task_directory',
        type=str,
        help='''Directory that the module containing the custom Task class
        resides in. This directory will be added to sys.path.''')
    pipeline_parser.add_argument(
        '-w', '--num_workers',
        type=int,
        default=1,
        help='''Set the number of workers to use. The default is 1.''')
    pipeline_parser.add_argument(
        '-l', '--log_level',
        type=str,
        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help='''Set luigi's log level. Default is ERROR, which should at least
        provide a starting point if something breaks down.''')
    pipeline_parser.set_defaults(func=pipeline_tool)


def pipeline_tool(parser, args):
    import os
    import sys

    import luigi

    from lib5c.contrib.luigi.pipeline import PipelineTask
    from lib5c.contrib.luigi.config import drop_config_file

    if not os.path.exists('luigi.cfg'):
        print 'no luigi.cfg found in current directory'
        print 'dropping example luigi.cfg file...'
        drop_config_file()
    else:
        local_scheduler = not args.remote_scheduler
        cmdline_args = ['--workers', str(args.num_workers),
                        '--log-level', args.log_level]
        if args.task_class is None:
            main_task_cls = PipelineTask
            luigi.run(cmdline_args=cmdline_args,
                      main_task_cls=main_task_cls,
                      local_scheduler=local_scheduler)
        else:
            if args.task_directory is not None:
                sys.path.append(args.task_directory)
            mod, cls = args.task_class.rsplit('.', 1)
            cmdline_args.extend(['--module', mod, cls])
            luigi.run(cmdline_args=cmdline_args,
                      local_scheduler=local_scheduler)
