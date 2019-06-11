def get_acc(predictList, trueList):
    right = 0
    total = 0
    for pre, tru in zip(predictList, trueList):
        total += 1
        if pre == tru:
            right += 1
    acc = right / 1.0 / total
    return acc


def get_evaluation_f(predict, true):
    total = len(true)
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    '''
    TP:method says its positive and ground truth agrees
    TN:method says its negative and ground truth agrees
    FP:method says its positive  ground truth disagrees
    FN method says its negative ground truth disagrees
    '''
    for pre, tru in zip(predict, true):
        if pre == tru and pre == 'sing':
            TP += 1
        elif pre == tru and pre == 'nosing':
            TN += 1
        elif pre != tru and pre == 'sing':
            FP += 1
        elif pre != tru and pre == 'nosing':
            FN += 1
        else:
            raise ("error...")

    accuracy = (TP + TN) / 1.0 / total
    precision = TP / 1.0 / (TP + FP)
    recall = TP / 1.0 / (TP + FN)
    specificity = TN / 1.0 / (TN + FP)
    f1measure = 2 * precision * recall / 1.0 / (precision + recall)
    return accuracy, precision, recall, f1measure, specificity
