import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (confusion_matrix,
                             precision_recall_curve)
import itertools

class Prediction():
    def __init__(self, model, test):
        self.model = model
        self.test = test
        self.pred = None
        self.mse = None
        self.mse_avg = None
        self.cm = None

    def make_prediction(self):
        self.pred = self.model.predict(self.test)
        diff = np.abs(self.pred - self.test)
        self.mse = np.mean(diff, axis=1)
        self.mse_avg = np.mean(self.mse, axis=1)

    def plot_avg_reconstruction_error(self, label_list, threshold_fixed = 0.3):
        error_df = pd.DataFrame({'Reconstruction_error': self.mse_avg, 'True_class': label_list})
        groups = error_df.groupby('True_class')
        fig, ax = plt.subplots()
        for name, group in groups:
            ax.plot(group.index, group.Reconstruction_error, marker='o', ms=3.5, linestyle='',
                    label="Break" if name == 1 else "Normal")
        ax.hlines(threshold_fixed, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
        ax.legend()
        plt.title("Reconstruction error for different classes")
        plt.ylabel("Reconstruction error")
        plt.xlabel("Data point index")
        plt.show();

    def plot_error_one_feature(self,featurenum, collst,
                               label_list, threshold_fixed = 0.3):
        error_df = pd.DataFrame({'Reconstruction_error': self.mse[:, featurenum],
                                 'True_class': label_list})
        groups = error_df.groupby('True_class')
        fig, ax = plt.subplots()

        for name, group in groups:
            ax.plot(group.index, group.Reconstruction_error, marker='o', ms=3.5, linestyle='',
                    label="Break" if name == 1 else "Normal")
        #ax.hlines(threshold_fixed, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
        ax.legend()
        plt.title("Reconstruction error for Feature " + str(collst[featurenum]))
        plt.ylabel("Reconstruction error")
        plt.xlabel("Data point index")
        plt.show();

    def plot_error_all_features(self, collst, label_list):
        for idx in list(range(0,len(collst))):
            self.plot_error_one_feature(idx, collst,label_list)

    def plot_pr_diagram(self, label_list, timestep):
        error_df = pd.DataFrame({'Reconstruction_error': self.mse_avg,
                                 'True_class': label_list[timestep:]})

        precision_rt, recall_rt, threshold_rt = precision_recall_curve(error_df.True_class,
                                                                       error_df.Reconstruction_error)
        plt.plot(threshold_rt, precision_rt[1:], label="Precision", linewidth=5)
        plt.plot(threshold_rt, recall_rt[1:], label="Recall", linewidth=5)
        # plt.xlim([0.23, 0.27])
        plt.title('Precision and recall for different threshold values')
        plt.xlabel('Threshold')
        plt.ylabel('Precision/Recall')
        plt.legend()
        plt.show()

    def performance(self,trh, label_list, timestep):
        z_scores = self.mse_avg
        outliers = z_scores > trh
        outliers
        print('The number of malicous blocks is: ' + str(label_list.count(1)) +
              ' The number of normal blocks: ' + str(label_list.count(0)))

        self.cm = confusion_matrix(label_list[timestep:], outliers)

        # true/false positives/negatives
        (tn, fp,
         fn, tp) = self.cm.flatten()
        pre = tp / (fp + tp)
        re = tp / (fn + tp)
        print(f"""The classifications using the MAD method with threshold={trh} are as follows:
        {self.cm}

        % of transactions labeled as fraud that were correct (precision): {tp}/({fp}+{tp}) = {tp / (fp + tp):.2%}
        % of fraudulent transactions were caught succesfully (recall):    {tp}/({fn}+{tp}) = {tp / (fn + tp):.2%}
        Accuracy: {(tp + tn) / (fn + tn + fp + tp):.2%} 
        F1 Score: {2 * ((pre * re) / (pre + re))}""")


    def plot_confusion_matrix(self,
                              target_names,
                              title='Confusion matrix',
                              cmap=None,
                              normalize=True):
        """
        Fork from: https://www.kaggle.com/grfiv4/plot-a-confusion-matrix
        given a sklearn confusion matrix (cm), make a nice plot

        Arguments
        ---------
        cm:           confusion matrix from sklearn.metrics.confusion_matrix

        target_names: given classification classes such as [0, 1, 2]
                      the class names, for example: ['high', 'medium', 'low']

        title:        the text to display at the top of the matrix

        cmap:         the gradient of the values displayed from matplotlib.pyplot.cm
                      see http://matplotlib.org/examples/color/colormaps_reference.html
                      plt.get_cmap('jet') or plt.cm.Blues

        normalize:    If False, plot the raw numbers
                      If True, plot the proportions

        Usage
        -----
        plot_confusion_matrix(cm           = cm,                  # confusion matrix created by
                                                                  # sklearn.metrics.confusion_matrix
                              normalize    = True,                # show proportions
                              target_names = y_labels_vals,       # list of names of the classes
                              title        = best_estimator_name) # title of graph

        Citiation
        ---------
        http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html

        """
        accuracy = np.trace(self.cm) / float(np.sum(self.cm))
        misclass = 1 - accuracy

        if cmap is None:
            cmap = plt.get_cmap('Blues')

        plt.figure(figsize=(8, 6))
        plt.imshow(self.cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()

        if target_names is not None:
            tick_marks = np.arange(len(target_names))
            plt.xticks(tick_marks, target_names, rotation=45)
            plt.yticks(tick_marks, target_names)

        if normalize:
            self.cm = self.cm.astype('float') / self.cm.sum(axis=1)[:, np.newaxis]

        thresh = self.cm.max() / 1.5 if normalize else self.cm.max() / 2
        for i, j in itertools.product(range(self.cm.shape[0]), range(self.cm.shape[1])):
            if normalize:
                plt.text(j, i, "{:0.4f}".format(self.cm[i, j]),
                         horizontalalignment="center",
                         color="white" if self.cm[i, j] > thresh else "black")
            else:
                plt.text(j, i, "{:,}".format(self.cm[i, j]),
                         horizontalalignment="center",
                         color="white" if self.cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
        plt.show()