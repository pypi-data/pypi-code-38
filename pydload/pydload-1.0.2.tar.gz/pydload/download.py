import requests
import progressbar
import time

mb = 1024 * 1024

def dload(url, save_to_path, timeout=10, max_time=30):
    request = requests.get(url, timeout=timeout, stream=True)

    file_size = (float(request.headers['Content-length'])// mb) + 1

    is_stopped = False

    with open(save_to_path, 'wb') as f:
        start_time = time.time()
        for chunk in progressbar.progressbar(request.iter_content(mb), max_value=file_size, prefix='MB'):
            f.write(chunk)
            if time.time() - start_time >= max_time:
                is_stopped = True
                break
    
    if is_stopped:
        print('Stopped due to excess time')
        return False
    
    else:
        print('Succefully Downloaded to:', save_to_path)
        return True
