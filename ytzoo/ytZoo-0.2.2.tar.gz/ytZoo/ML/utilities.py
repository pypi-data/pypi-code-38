import pandas as pd
from sklearn.model_selection import cross_validate
import matplotlib.pyplot as plt

def calculate_lift(ytrue, yproba, cumulative=True):
    cmp = pd.DataFrame(yproba, columns=['pred'])
    cmp.loc[:, 'y'] = ytrue

    last_value = 1
    deciles = np.linspace(0, 1, 11)[::-1][1:]
    r = []
    for k in deciles:
        value = cmp.pred.quantile(k)
        if cumulative:
            selection = cmp.loc[cmp.pred >= value, :]
        else:
            selection = cmp.loc[(cmp.pred >= value) &
                                (cmp.pred <= last_value), :]
            last_value = value
        num_true = (selection.y == 1).sum()
        num_total = selection.shape[0]
        rprate = num_true / num_total
        r.append(dict(cutoff=value,
                      decile=k,
                      responserate=rprate,
                      num_true=num_true,
                      num_total=num_total))
    lift = pd.DataFrame(r)
    bs_num_true = (cmp.y == 1).sum()
    bs_num_total = cmp.shape[0]
    bs_rprate = bs_num_true / bs_num_total
    lift['baseline'] = bs_rprate
    lift['lift'] = lift.responserate / bs_rprate
    return lift

def plot_lift(ytrue, yproba, cumulative=True):
    import matplotlib.ticker as ticker
    lift = calculate_lift(ytrue, yproba, cumulative)
    grp = 10 - lift.decile*10
    drr = lift.responserate
    rrr = lift.baseline
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(grp, drr, marker='o', color='blue', lw=1.5)
    line2, = ax.plot(grp, rrr, ls='dashed', color='gray', lw=1.5)

    xtext = ax.set_xlabel('Deciles')
    ytext = ax.set_ylabel('% Response')

    ax.set_xlim(0.5, 9.5)
    ax.set_xticks(range(1, 11, 1))

    ax.set_ylim(0, max(drr)*(1.1))
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda t1, _: '{:.0%}'.format(t1)))

    txt1 = str("Decile 1 R.R.: " + '{:.1%}'.format(
        drr.loc[0]) + "; Lift: " + '{:3.2}'.format(drr.loc[0]/rrr.loc[0]))
    txt2 = str("Decile 2 R.R.: " + '{:.1%}'.format(
        drr.loc[0]) + "; Lift: " + '{:3.2}'.format(drr.loc[1]/rrr.loc[1]))
    txt3 = str("Decile 3 R.R.: " + '{:.1%}'.format(
        drr.loc[0]) + "; Lift: " + '{:3.2}'.format(drr.loc[2]/rrr.loc[2]))

    plt.text(grp[1]-0.7, drr.loc[0]*0, 99, txt1,
             ha='left', rotation=0, wrap=True)
    plt.text(grp[2]-0.7, drr.loc[0]*0, 99, txt2,
             ha='left', rotation=0, wrap=True)
    plt.text(grp[3]-0.7, drr.loc[0]*0, 99, txt3,
             ha='left', rotation=0, wrap=True)

    plt.legend((line1, lin2), ('Model', 'Baseline'),
               loc='upper right', bbox_to_anchor=[0.95, 0.95], shadow=True)

    if cumulative:
        plt.suptitle('Cumulative Lift Chart', fontsize=14)
    else:
        plt.suptitle('Stratified Lift Chart', fontsize=14)
    plt.show()

def plot_confusion_matrix(ytrue,
                          ypred,
                          classes=None,
                          normalize=True,
                          cmap=None):
    cmap = plt.cm.Blues if not cmap else cmap
    cm = confusion_matrix(ytrue, ypred)
    if not classes:
        n = len(set(ytre))
        classes = list(range(n))
    if normalize:
        title = 'Normalized Confusion Matrix'
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    else:
        title = 'Frequency Confusion Matrix'
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment='center',
                 color='white' if cm[i, j] > thresh else 'black')

    plt.ylabel("True label")
    plt.xlabel('Predicted label')
    plt.tight_layout()


def kfold_cv(model, X, y, cv, verbose=1, shuffle=False):
    from sklearn.metrics import mean_squared_error
    return kfold_cvx(model, X, y, cv, 
            f_metric=mean_squared_error,
            verbose=verbose,
            shuffle=shuffle)

def kfold_cvx(model,
             X,
             y,
             cv,
             f_metric=mean_squared_error,
             verbose=1,
             shuffle=False):
    from copy import deepcopy
    from sklearn.model_selection import KFold
    kf = KFold(n_splits=cv, shuffle=shuffle)
    kfscores = []
    for i, (train_index, test_index) in enumerate(kf.split(X)):
        if verbose:
            print("processing cv batch {} of {}".format(i+1, cv), end=' ')
        mdl = deepcopy(model)
        X_train, X_test = X.loc[train_index], X.loc[test_index]
        y_train, y_test = y[train_index], y[test_index]
        mdl.fit(X_train, y_train)
        
        y_train_pred = mdl.predict(X_train)
        trainscore = f_metric(y_train, y_train_pred)
        
        y_test_pred = mdl.predict(X_test)
        testscore = f_metric(y_test, y_test_pred)
        scores = {'train': trainscore, 'test':testscore}
        print("scores: train {}, test {}".format(trainscore, testscore))
        kfscores.append(scores)
    rst = pd.DataFrame(kfscores)
    stats = rst.describe().loc[['min', 'mean', 'std', 'max']] 
    return pd.concat([rst, stats])

def plot_history(history ,figsize=(4,2)):
    """Plot Keras training history"""
    loss_list = [s for s in history.history.keys() if 'loss' in s and 'val' not in s]
    val_loss_list = [s for s in history.history.keys() if 'loss' in s and 'val' in s]
    acc_list = [s for s in history.history.keys() if 'acc' in s and 'val' not in s]
    val_acc_list = [s for s in history.history.keys() if 'acc' in s and 'val' in s]

    if len(acc_list)==0:
        fig, axloss = plt.subplots(1, figsize=(figsize[0], figsize[1]/2))
        axloss.set_xlabel('Epochs')
    else:
        fig, (axloss, axacc) = plt.subplots(2, sharex=True, figsize=figsize)
        axacc.set_ylim(0,1)

    ## As loss always exists
    epochs = range(1,len(history.history[loss_list[0]]) + 1)
    
    ## Loss
    for l in loss_list:
        axloss.plot(epochs, history.history[l], 'b', label='Training loss (' + str(str(format(history.history[l][-1],'.5f'))+')'))
    for l in val_loss_list:
        axloss.plot(epochs, history.history[l], 'g', label='Validation loss (' + str(str(format(history.history[l][-1],'.5f'))+')'))

    axloss.set_ylabel('Loss')
    axloss.legend(bbox_to_anchor=(1.04,1), loc="upper left")
    
    if len(acc_list)>0:
        ## Accuracy
        for l in acc_list:
            axacc.plot(epochs, history.history[l], 'b', label='Training accuracy (' + str(format(history.history[l][-1],'.5f'))+')')
        for l in val_acc_list:    
            axacc.plot(epochs, history.history[l], 'g', label='Validation accuracy (' + str(format(history.history[l][-1],'.5f'))+')')

        axacc.set_xlabel('Epochs')
        axacc.ylabel('Accuracy')
        axacc.legend(bbox_to_anchor=(1.04,1), loc="upper left")
