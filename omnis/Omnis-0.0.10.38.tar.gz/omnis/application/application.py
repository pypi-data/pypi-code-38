import platform


class Application:

    def __init__(self):
        try:
            self.os_type = platform.system()
        except Exception as e:
            print("Application initialize failed")
            raise e
        # default setting for using 1gpu and gpu_ids for 0
        self.gpu_num = 1
        self.gpu_ids = [0]
        self.deepblock_log = False

    def use_specific_gpus(self, gpu_ids):
        self.gpu_ids = gpu_ids
        self.gpu_num = len(gpu_ids)

    def use_deepblock_site_log(self, use_or_not=False):
        self.deepblock_log = use_or_not
