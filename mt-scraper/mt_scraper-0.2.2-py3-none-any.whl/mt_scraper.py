import traceback
import threading
import argparse
import os.path
import random
from urllib.request import urlopen, Request
#from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
from datetime import date, datetime
from time import sleep
from json import dump, load
from queue import Queue
from sys import stdout, stderr

from .dummy_parser import MyDummyHTMLParser

__version__ = '0.2.2'

def default_json(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()

class Command():
    pass


class ExitCommand(Command):
    '''СИгнал для выхода потоку-потребителю'''
    pass


class GetCommand(Command):
    def __init__(self, num, obj):
        self.__num = num
        self.__obj = obj

    @property
    def num(self):
        return self.__num

    @property
    def obj(self):
        return self.__obj

    def __str__(self):
        return 'CMD: Get num:{}'.format(self.num)


class Scraper:
    '''Scrapper base class'''
    description = 'Scrapper for http://example.com/'
    filedir = None
    out_filename = 'out.json'
    threads_num = 5
    queue_len = 5
    url_template = '{}'
    url_components_list = ['http://example.com/', 'http://scraper.iamengineer.ru', 'http://scraper.iamengineer.ru/bad-file.php', 'http://badlink-for-scarper.ru',]

    #worker_outstring = '{thread_name:10}ID:{num:7}\t{success} {additional_info}'
    worker_outstring = '{thread_name:10}ID:{num:7}\t{success}'

    headers={'User-Agent': 'Python Scraper V{}'.format(__version__)}
    use_proxy = False

    def parse(self, num, url_component, html):
        '''Необходимо переопределить этот метод
        Должен возвращять словарь или None, если парсинг странички
        невозможен 
        '''
        #return {'ID':url_component, 'h1':'FAKE'}
        #return None
        parser = MyDummyHTMLParser()
        parser.feed(html)
        obj = parser.obj
        obj['url_component'] = url_component
        return parser.obj

    def get_url(self, obj):
        '''Необходимо переопределить этот метод
        если вам нужно особое формирование URL 
        '''
        return self.url_template.format(obj) 

    def get_url_component_list(self):
        '''Необходимо переопределить этот метод
        если вам нужно особое формирование списка
        компонентов URL, например получить его из файла
        из коммандной строки 
        '''
        return self.url_components_list

    def add_arguments(self, parser):
        '''Необходимо переопределить этот метод
        если вам нужно добавить собственные аргументы
        коммандной строки, например особой загрузки списка
        компонентов URL или для формирования
        '''
        pass

    def __init__(self):
        self.obj_list = []
        self.proxies = []

        self.queue = Queue(maxsize=self.queue_len)

        self.obj_list_mutex = threading.Lock()
        self.stdout_mutex = threading.Lock()
        if self.filedir is None:
            self.filedir = os.path.dirname(os.path.abspath(__file__))


    # def load_proxy(self, filename):
    #     proxies = []
    #     with open(filename) as infile:
    #         lines = infile.readlines()

    #     for line in lines:
    #         proxies.append(line.strip())

    #     return proxies


    def get_html(self, url):
        #proxies = {'HTTP': random.choice(proxies)}

        req = Request(url=url, method='GET', headers=self.headers)
        # if use_proxy:
        #     req.set_proxy(random.choice(proxies), 'HTTP')
        f = urlopen(req)
        list_html = f.read().decode('utf-8', errors='ignore')

        return list_html

    def worker(self):
        '''This is worker thread. It gets html and execute parsing function.
        Exit then recive object of ExitCommand class'''
        thread_name = threading.currentThread().getName()

        if not self.args.machine_out:
            with self.stdout_mutex:
                print('Worker started', thread_name)

        out_string_data = {'thread_name':thread_name}

        while True:
            command =  self.queue.get()
            #print('GET COMMAND', command)
            if not isinstance(command, Command):
                raise ValueError('Unknown command')

            if isinstance(command, ExitCommand):
                break

            num = command.num
            out_string_data['num'] = num
            obj = command.obj
            url = self.get_url(obj)
            try:
                html = self.get_html(url)
                obj_out = self.parse(num, obj, html)
                with self.obj_list_mutex:
                    self.obj_list.append(obj_out)

                out_string_data['success'] = 'OK'
                #out_string_data['additional_info'] = ''


            except HTTPError as e:
                out_string_data['success'] = str(e) 
                #out_string_data['additional_info'] = str(e)

            except URLError as e:
                out_string_data['success'] = 'URL Error: {}'.format(e.reason) 
                #out_string_data['additional_info'] = str(e)

            except Exception as e:
                out_string_data['success'] = str(e) 
                #out_string_data['additional_info'] = str(e)

                with self.stdout_mutex:
                    traceback.print_exc(file=stderr)

            with self.stdout_mutex:
                print(self.worker_outstring.format(**out_string_data))


        if not self.args.machine_out:
            with self.stdout_mutex:
                print('Worker STOPPED', thread_name)


    def __add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file-name', 
            default=self.out_filename, 
            help="Filename for input and output data. '\
            'May be stdout for console output"
        )
        parser.add_argument(
            '-t',
            '--threads',
            type=int,
            default=self.threads_num, 
            help="Number of threads"
        )
        parser.add_argument(
            '-q',
            '--queue-len', 
            default=self.queue_len, 
            help="Length of queue for requests"
        )
        # parser.add_argument(
        #     '-p',
        #     '--use-proxy',
        #     const=use_proxy,
        #     default=not use_proxy,
        #     action='store_const',
        #     help="Please use proxy servers from list"
        # )
        parser.add_argument(
            '-m', 
            '--machine-out', 
            action='store_true',
            help='Prohibit the printing of unnecessary information in std. '\
            'This flag is used to output information to standard output '\
            'instead of a file.'
        )

        self.add_arguments(parser)


    def run(self, cmd_args=None):
        parser = argparse.ArgumentParser(description=self.description)
        self.__add_arguments(parser)
        args = parser.parse_args(args=cmd_args)
        # proxies = load_proxy(os.path.join(filedir, 'proxy.txt'))
        #print(proxies)
        #print(args)
        #raise KeyboardInterrupt

        out_filename = args.file_name
        threads_num = args.threads
        queue_len = args.queue_len
        # use_proxy = args.use_proxy

        self.args = args

        self.url_components_list = self.get_url_component_list()

        try:
            with open(out_filename) as infile:
                self.obj_list = load(infile)
        except FileNotFoundError:
            self.obj_list = []

        start_time = datetime.now()    

        if not self.args.machine_out:
            print('start working with:', self.description)
            print('Work with {} threads at {}'.format(threads_num, start_time))
            print('Push Ctrl+C for exit')

        threads = []
        url_components_list = self.get_url_component_list()
        obj_iter = iter(enumerate(url_components_list))

        for i in range(threads_num):
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)
        try:
            while True:
                (num, obj, ) = next(obj_iter)
                self.queue.put(GetCommand(num, obj))

        except StopIteration:

            if not self.args.machine_out:
                 with self.stdout_mutex:
                    print('End of operation')

        except KeyboardInterrupt:
            if not self.args.machine_out:
                with self.stdout_mutex:
                    print('Operation canceled by keyboard')

        #New line for stdout parsing
        print()
           
        for i in range(threads_num):
            self.queue.put(ExitCommand())

        for thread in threads:
            thread.join(timeout=60)

        zths = []
        for th in threads:
            if th.is_alive():
                zths.append(th)

        stop_time = datetime.now()
        if not self.args.machine_out:
            print('Zombies:')
            print(zths)
            print('Processed in', stop_time - start_time)
        
        try:
            if out_filename == 'stdout':
                outfile = stdout
            else:
                outfile = open(out_filename, 'w')

            dump(
                self.obj_list, 
                outfile,
                indent=4,
                default=default_json,
                sort_keys=True
            )
        finally:
            if out_filename != 'stdout':
                outfile.close()

        if not self.args.machine_out:
            print('Saved at', out_filename, datetime.now())

def main():
    print('Hello World!')
    scraper = Scraper()
    scraper.run()

if __name__ == '__main__':
    main()