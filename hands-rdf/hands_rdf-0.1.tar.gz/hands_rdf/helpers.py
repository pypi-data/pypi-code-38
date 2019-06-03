from sklearn.metrics import cohen_kappa_score, classification_report, precision_recall_fscore_support


def show_stats(y_test, res):

    print(classification_report(y_test, res))
    precision, recall, f1, support = precision_recall_fscore_support(y_test, res, average='weighted', pos_label=True)
    avg_scores = precision_recall_fscore_support(y_test, res,
                                                 average="weighted")
    cohenKappa = cohen_kappa_score(y_test, res)
    print(avg_scores)

    print("Cohen kappa score: " + str(cohenKappa))
    return {
        "F1": f1,
        "Recall(TPR)": recall,
        "Precision": precision,
        "Precision_avg": str(avg_scores[0]),
        "Recall_avg": str(avg_scores[1]),
        "F1_avg": str(avg_scores[2]),
        "Support_total": str(avg_scores[3]),
        "cohen_kappa": cohenKappa
    }
