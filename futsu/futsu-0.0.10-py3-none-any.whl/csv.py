import csv

def read_csv(fn):
    col_name_list = None
    ret = []
    with open(fn,'r') as fin:
        for line in csv.reader(fin):
            if col_name_list is None:
                col_name_list = list(line)
            else:
                if((len(col_name_list)==1) and (len(line)==0)):
                     line = ['']
                assert(len(line)==len(col_name_list))
                ret.append({col_name_list[i]:line[i] for i in range(len(col_name_list))})
    return ret, col_name_list

def write_csv(fn,v_dict_list,col_name_list=None,sort_key_list=None):
    if col_name_list is None:
        assert(len(v_dict_list)>0)
        col_name_list = list(sorted(v_dict_list[0].keys()))
    if sort_key_list is not None:
        t_list = [ ( \
                    tuple(v_dict[c] for c in sort_key_list), \
                    tuple(v_dict[c] for c in col_name_list), \
                    v_dict, \
                    ) for v_dict in v_dict_list ]
        t_list = sorted(t_list)
        v_dict_list = [ t[2] for t in t_list ]
    with open(fn,'w') as fout:
        csv_out = csv.writer(fout)
        csv_out.writerow(col_name_list)
        for v_dict in v_dict_list:
            csv_out.writerow([v_dict[col_name] for col_name in col_name_list])
