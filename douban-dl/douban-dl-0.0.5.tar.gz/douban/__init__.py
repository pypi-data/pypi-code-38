from concurrent.futures import ThreadPoolExecutor

threadPoolExecutor = ThreadPoolExecutor(max_workers=5, thread_name_prefix='downloader')
