import random


def split_data(sent_list, train=0.90, dev=0.00):
    random.shuffle(sent_list)

    sent_list_len = len(sent_list)

    train_set_len = int(sent_list_len * train)
    dev_set_len = int(sent_list_len * dev)
    test_set_len = sent_list_len - train_set_len - dev_set_len

    train_set = sent_list[:train_set_len]
    dev_set = sent_list[train_set_len: train_set_len + dev_set_len]
    test_set = sent_list[- test_set_len:]

    return train_set, dev_set, test_set
