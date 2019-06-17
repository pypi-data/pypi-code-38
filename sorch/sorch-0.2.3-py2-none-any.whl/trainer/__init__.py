import torch
import os


class EasyModule(torch.nn.Module):
    def e_save(self, save_dir, step=1):
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        torch.save(self.state_dict(), os.path.join(save_dir, 'model-%d.ckpt'%step))


    def e_restore(self, save_dir, step=1):
        p = os.path.join(save_dir, 'model-%d.ckpt' % step)
        if not os.path.exists(p):
            print('Could not find any checkpoint at %s, skipping restore' % p)
            return
        self.load_state_dict(torch.load(p))

torch.nn.Module.save = EasyModule.e_save
torch.nn.Module.restore = EasyModule.e_restore