
"""
Evaluate Ada Boost classifier
"""
import numpy as np
import pandas as pd

from sklearn.ensemble import AdaBoostClassifier
from algo_evaluation.datasets import split_dataset, load_higgs_train
from algo_evaluation import LOGGER


class AdaBoost:
    def __init__(self, data, n_estimators=50, learning_rate=1.0):
        features, weights, labels = data
        self.clf = AdaBoostClassifier(n_estimators=n_estimators, learning_rate=learning_rate)
        LOGGER.info('Created Ada Boost classifier with params {}'.format({'n_estimators': n_estimators,
                                                                          'learning_rate': learning_rate}))
        self.predictions, self.trnaccuracy, self.tstaccuracy = None, None, None
        self.dataset = split_dataset(features, weights, labels)

    def train(self):
        """
        Train Ada Boost on the higgs dataset
        """
        self.clf = self.clf.fit(self.dataset['training']['features'], self.dataset['training']['labels'])
        LOGGER.info('Trained Ada Boost classifier')

    def predict(self):
        """
        Predict label using Ada Boost
        :return:
        """
        self.predictions = self.clf.predict(self.dataset['test']['features'])
        LOGGER.info('Generated predictions')

    def evaluate(self):
        self.trnaccuracy = self.clf.score(self.dataset['training']['features'],
                                          self.dataset['training']['labels'],
                                          sample_weight=self.dataset['training']['weights'])
        self.tstaccuracy = self.clf.score(self.dataset['test']['features'],
                                          self.dataset['test']['labels'],
                                          sample_weight=self.dataset['test']['weights'])
        LOGGER.info('Training Weighted Accuracy score = %s', self.trnaccuracy)
        LOGGER.info('Test Weighted Accuracy score = %s', self.tstaccuracy)


def run_AdaBoost(data, n_estimators=50, learning_rate=1.0):
    """
    Run and evaluate Ada Boost with default settings
    """
    dt = AdaBoost(data=data, n_estimators=n_estimators, learning_rate=learning_rate)
    dt.train()
    dt.predict()
    dt.evaluate()
    return dt.trnaccuracy, dt.tstaccuracy


def estimate_best_n_estimators():
    """
    Run Ada Boost classifier with multiple settings of
    n_estimators and plot the accuracy function of n_estimators
    :return: the best n_estimators setting
    """
    n_estimators_range = np.arange(1, 50, 2)
    data = load_higgs_train()
    records = [[n_estimator] + list(run_AdaBoost(data=data, n_estimators=n_estimator))
               for n_estimator in n_estimators_range]
    LOGGER.info('Performed evaluation of the n_neighbours setting choice')
    columns = ['n_neighbours', 'training_score', 'test_score']
    df = pd.DataFrame.from_records(records, columns=columns, index=columns[0])
    LOGGER.info(df)
    return df


def plot_accuracy_function(df):
    smooth_df = pd.rolling_mean(df, 5)
    smooth_df.plot(title='Accuracy change as a function of n_neighbours (smoothed)')