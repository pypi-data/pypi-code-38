import requests
import time
import travel_backpack


class Request:
    def run(self, method, url, *args, retry_count=-1, wait_time=5, asynchronous=True, **kwargs):
        if asynchronous:
            travel_backpack.thread_encapsulation(self.run)(
                method, url, *args, retry_count=retry_count, wait_time=wait_time, asynchronous=False, **kwargs)
            return
        else:
            retry = True
            print('REST request:', method, url, args, kwargs)
            while retry:
                try:
                    requests.request(method, url)
                    retry = False
                except requests.exceptions.ConnectionError as e:
                    #print(e)
                    print('.')
                    if retry_count == 0:
                        retry = False
                    else:
                        retry_count -= 1
                        time.sleep(wait_time)
                        retry = True


actions = {'rest request': Request}

if __name__ == '__main__':
    import sys
    Request().run(*sys.argv[1:])