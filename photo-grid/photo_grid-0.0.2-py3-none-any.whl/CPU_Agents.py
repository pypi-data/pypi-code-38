from enum import Enum
import pandas as pd
import numpy as np

class Dir(Enum):
    NORTH=0
    WEST=1
    SOUTH=2
    EAST=3

class Field():
    def __init__(self, img_raw, img_bin, map, nc, nr, anchors):
        '''
        '''
        self.img_raw = img_raw
        self.img_bin = img_bin
        self.img_binsm = self.denoise(self.img_bin, 30)
        self.map = map
        self.anchors = anchors
        self.px_H, self.px_W = img_bin.shape[0], img_bin.shape[1]
        self.nrow, self.ncol = nr, nc
        self.n_ch = img_raw.shape[2]
        self.agents = []
        self.cpu_seg()
    def cpu_seg(self, coef_grid=.2, center=0):
        self.agents = []
        self.set_anchors(center=center)
        self.cpu_pre_dim()
        self.cpu_bound(coef_grid=coef_grid)
    def set_anchors(self, center=0):
        '''
        '''
        idx = 0
        idx_name = 1
        for row in range(self.nrow): # then y
            agents_row = []
            for col in range(self.ncol): # start from x
                # get name
                try:
                    name = self.map.iloc[row, col]
                except:
                    name = "id_%d" %(idx_name)
                    idx_name += 1
                # initialize agent
                agent = Agent(name, row, col)
                px_anchors = self.anchors[idx]
                # set position
                pos_x = int(px_anchors['x'])
                pos_y = int(px_anchors['y'])
                agent.set_coordinate(x=pos_x, y=pos_y)
                # see if reduncdent
                rg_x = 20
                rg_y = 20
                try:
                    sc_W = self.img_binsm[(pos_y-rg_y):(pos_y+rg_y), (pos_x-rg_x):pos_x].sum()
                except:
                    sc_W = 0
                try:
                    sc_E = self.img_binsm[(pos_y-rg_y):(pos_y+rg_y), pos_x:(pos_x+rg_x)].sum()
                except:
                    sc_E = 0
                try:
                    sc_N = self.img_binsm[(pos_y-rg_y):pos_y, (pos_x-rg_x):(pos_x+rg_x)].sum()
                except:
                    sc_N = 0
                try:
                    sc_S = self.img_binsm[pos_y:(pos_y+rg_y), (pos_x-rg_x):(pos_x+rg_x)].sum()
                except:
                    sc_S = 0
                # print((sc_W+sc_E+sc_N+sc_S)/(rg_x*rg_y*8))
                if ((sc_W+sc_E+sc_N+sc_S)/(rg_x*rg_y*8))>=center:
                    agent.set_save(save=True)
                # output agent
                agents_row.extend([agent])
                idx += 1
            self.agents.extend([agents_row])
    def cpu_pre_dim(self, tol=5):
        '''
        '''
        img = self.img_binsm
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent_self = self.get_agent(row, col)
                rg_temp = dict()
                for axis in [0, 1]:
                    # extract direction info and 1dImg
                    dir_1 = Dir(axis) # axis:0, return N(0) and S(2)
                    dir_2 = Dir(axis+2) # axis:1, return W(1) and E(3)
                    axis_rev = (not axis)*1
                    img_1d = img[agent_self.y, :] if axis else img[:, agent_self.x]
                    # extract agents info
                    pt_self = agent_self.get_coordinate()[axis_rev]
                    agent_neig1 = self.get_agent_neighbor(row, col, dir_1)
                    agent_neig2 = self.get_agent_neighbor(row, col, dir_2)
                    # if both neighbors exists
                    if (agent_neig1!=0) & (agent_neig2!=0):
                        pt_neig1 = agent_neig1.get_coordinate()[axis_rev]
                        pt_neig2 = agent_neig2.get_coordinate()[axis_rev]
                        pt_mid = int((pt_neig1+pt_neig2)/2)
                        pt_bd1 = int((pt_neig1+pt_mid)/2)
                        pt_bd2 = int((pt_neig2+pt_mid)/2)
                    # if only left/up side exist
                    elif agent_neig1:
                        pt_neig1 = agent_neig1.get_coordinate()[axis_rev]
                        pt_bd1 = int((pt_self+pt_neig1)/2)
                        pt_bd2 = img.shape[axis]
                        agent_self.set_border(dir_2, pt_bd2)
                    # if only right/down side exist
                    elif agent_neig2:
                        pt_neig2 = agent_neig2.get_coordinate()[axis_rev]
                        pt_bd1 = 0
                        pt_bd2 = int((pt_self+pt_neig2)/2)
                        agent_self.set_border(dir_1, pt_bd1)
                    # if neither side exist
                    else:
                        pt_bd1 = 0
                        pt_bd2 = img.shape[axis]
                        agent_self.set_border(dir_1, pt_bd1)
                        agent_self.set_border(dir_2, pt_bd2)
                    # negative side (neighber 1)
                    pt_cur = pt_self
                    tol_cur = 0
                    while (tol_cur < tol) & (pt_cur > pt_bd1):
                        try:
                            img_val = img_1d[pt_cur]
                        except:
                            break
                        tol_cur += 1 if img_val==0 else -tol_cur #else reset to 0
                        pt_cur -= 1
                    rg_temp[dir_1.name] = pt_cur
                    # positive side (neighber 2)
                    pt_cur = pt_self
                    tol_cur = 0
                    while (tol_cur < tol) & (pt_bd2 > pt_cur):
                        try:
                            img_val = img_1d[pt_cur]
                        except:
                            break
                        tol_cur += 1 if img_val==0 else -tol_cur #else reset to 0
                        pt_cur += 1
                    rg_temp[dir_2.name] = pt_cur
                agent_self.set_pre_dim(rg_temp)
                # print("==== row:%d, col:%d ====" %(row, col))
                # print(rg_temp)
    def cpu_bound(self, coef_grid=.2):
        '''
        '''
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent_self = self.get_agent(row, col)
                save_self = 0 if agent_self.save else -999
                for dir in list([Dir.EAST, Dir.SOUTH]):
                    agent_neig = self.get_agent_neighbor(row, col, dir)
                    dir_neig = list(Dir)[(dir.value+2)%4] # reverse the direction
                    if agent_neig:
                        save_neig = 0 if agent_neig.save else -999
                        dist_agents = abs(agent_self.x-agent_neig.x) if dir==Dir.EAST else abs(agent_self.y-agent_neig.y)
                        while abs(agent_self.get_border(dir)-agent_neig.get_border(dir_neig))>1:
                            scA_self = agent_self.get_score_area(dir, self.img_bin)
                            scG_self = agent_self.get_score_grid(dir)/dist_agents
                            scA_neig = agent_neig.get_score_area(dir_neig, self.img_bin)
                            scG_neig = agent_neig.get_score_grid(dir_neig)/dist_agents
                            score_self = scA_self - (scG_self*coef_grid) + save_self
                            score_neig = scA_neig - (scG_neig*coef_grid) + save_neig
                            if score_self > score_neig:
                                agent_self.update_border(dir, 1)
                            elif score_self < score_neig:
                                agent_neig.update_border(dir_neig, -1)
                            else:
                                agent_self.update_border(dir, 1)
                                agent_neig.update_border(dir_neig, -1)
    def denoise(self, img, n_denoise=1):
        '''
        '''
        from scipy.signal import convolve2d
        k_blur = np.array((
            [1, 4, 1],\
            [4, 9, 4],\
            [1, 4, 1]), dtype='int')/29
        for i in range(n_denoise):
            img = convolve2d(img, k_blur, mode="same")
        img[img>0.5] = 1
        img[img<=0.5] = 0
        return img
    def get_agent(self, row, col):
        '''
        '''
        if (row<0) | (row>=self.nrow) | (col<0) | (col>=self.ncol):
            return 0
        else:
            return self.agents[row][col]
    def get_agent_neighbor(self, row, col, dir=Dir.NORTH):
        '''
        '''
        if dir==Dir.NORTH:
            return self.get_agent(row-1, col)
        elif dir==Dir.EAST:
            return self.get_agent(row, col+1)
        elif dir==Dir.SOUTH:
            return self.get_agent(row+1, col)
        elif dir==Dir.WEST:
            return self.get_agent(row, col-1)
    def get_DF(self):
        df = pd.DataFrame(columns=['var', 'row', 'col',\
                                   'border_N', 'border_W', 'border_S', 'border_E',\
                                   'area_all', 'area_veg'])
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row, col)
                entry = dict(var=agent.name, row=agent.row, col=agent.col,\
                             border_N=agent.get_border(Dir.NORTH),\
                             border_W=agent.get_border(Dir.WEST),\
                             border_S=agent.get_border(Dir.SOUTH),\
                             border_E=agent.get_border(Dir.EAST))
                rg_row = range(entry['border_N'], entry['border_S'])
                rg_col = range(entry['border_W'], entry['border_E'])
                img_bin_agent = self.img_bin[rg_row, :][:, rg_col]
                entry['area_all'] = len(rg_row)*len(rg_col)
                entry['area_veg'] = img_bin_agent.sum()
                df.loc[len(df)] = entry
        idx_na = pd.isna(df['var'].values)
        idx_keep = [not boo for boo in idx_na]
        df = df.loc[idx_keep,:]
        return df
    def get_index(self, ch_1, ch_2=-1, ch_3=-1, isSingle=False, isRatio=False, isContrast=False, isThree=False, name_index="index"):
        img_raw = self.img_raw.copy().astype(np.int)
        if img_raw.shape[2]==3 and ch_1==3:
            ch_1 = 1
        if isSingle:
            img_index = (img_raw[:,:,ch_1])
        if isRatio:
            img_index = img_raw[:,:,ch_1]/(img_raw[:,:,ch_2]+1e-8)
        if isContrast:
            img_index = (img_raw[:,:,ch_1]-img_raw[:,:,ch_2])/(img_raw[:,:,ch_1]+img_raw[:,:,ch_2]+1e-8)
        if isThree:
            img_index = (2*img_raw[:,:,ch_1]-img_raw[:,:,ch_2]-img_raw[:,:,ch_3])/(img_raw[:,:,ch_1]+img_raw[:,:,ch_2]+img_raw[:,:,ch_3]+1e-8)
        df = pd.DataFrame(columns=['var', 'index'])
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row, col)
                entry = dict(var=agent.name, index=0)
                rg_row = range(agent.get_border(Dir.NORTH), agent.get_border(Dir.SOUTH))
                rg_col = range(agent.get_border(Dir.WEST), agent.get_border(Dir.EAST))
                img_bin_agent = self.img_bin[rg_row, :][:, rg_col]
                img_index_agent = img_index[rg_row, :][:, rg_col]
                n_veg = img_bin_agent.sum()
                sum_index = np.multiply(img_bin_agent, img_index_agent).sum()
                entry['index'] = sum_index/(n_veg+1e-8)
                df.loc[len(df)] = entry
        df.columns = ['var', name_index]
        idx_na = pd.isna(df['var'].values)
        idx_keep = [not boo for boo in idx_na]
        df = df.loc[idx_keep,:]
        return df


class Agent():
    def __init__(self, name, row, col):
        '''
        '''
        self.name = name
        self.row, self.col = row, col
        self.y, self.x = 0, 0
        self.save = False
        self.pre_rg_W, self.pre_rg_H = range(0), range(0)
        self.border = dict()
        for dir in list([Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]):
            self.border[dir.name] = 0
    def get_col(self):
        '''
        '''
        return self.col
    def get_row(self):
        '''
        '''
        return self.row
    def get_coordinate(self):
        '''
        '''
        return self.x, self.y
    def get_pre_dim(self, isHeight=True):
        '''
        '''
        return self.pre_rg_H if isHeight else self.pre_rg_W
    def get_border(self, dir):
        return self.border[dir.name]
    def get_rect(self):
        from PyQt5.QtCore import QRect
        x = self.get_border(Dir.WEST)
        y = self.get_border(Dir.NORTH)
        w = self.get_border(Dir.EAST) - x
        h = self.get_border(Dir.SOUTH) - y
        return QRect(x, y, w, h)
    def get_score_area(self, dir, img):
        '''
        Will ragne from 0 to 1
        '''
        isH = dir.value%2 # E->1, S->0
        rg = self.get_pre_dim(isHeight=isH)
        bd = self.get_border(dir)
        # print("==== row:%d, col:%d ====" %(self.row, self.col))
        # print(rg)
        # print(bd)
        return img[rg, bd].mean() if isH else img[bd, rg].mean()
    def get_score_grid(self, dir):
        '''
        Will ragne from 0 to 1
        '''
        isWE = dir.value%2 # is W, E or N, S
        pt_center = self.x if isWE else self.y
        pt_cur = self.get_border(dir)
        return abs(pt_cur-pt_center)
    def set_coordinate(self, x, y):
        '''
        '''
        self.x = int(x)
        self.y = int(y)
        self.set_border(Dir.NORTH, y)
        self.set_border(Dir.SOUTH, y)
        self.set_border(Dir.WEST, x)
        self.set_border(Dir.EAST, x)
    def set_pre_dim(self, rg):
        '''
        '''
        self.pre_rg_W = range(rg['WEST'], rg['EAST'])
        self.pre_rg_H = range(rg['NORTH'], rg['SOUTH'])
        self.x = int((rg['EAST']+rg['WEST'])/2)
        self.y = int((rg['NORTH']+rg['SOUTH'])/2)
    def set_border(self, dir, value):
        '''
        '''
        self.border[dir.name] = int(value)
    def update_border(self, dir, value):
        '''
        '''
        self.border[dir.name] += int(value)
    def set_save(self, save=False):
        self.save = save
