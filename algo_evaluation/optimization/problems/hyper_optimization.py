
"""
Optimize classifier settings
"""
import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import cross_val_score
from algo_evaluation.optimization.hill_climbing import hillclimb
from algo_evaluation.optimization.simulated_annealing import simulated_annealing
from algo_evaluation.optimization.genetic_optimize import genetic_optimize
from algo_evaluation.optimization.mimic import Mimic

DEFAULT_EXPERIMENT_SETTINGS = dict()
DEFAULT_EXPERIMENT_SETTINGS['rhc'] = {'max_evaluations': 1000}
DEFAULT_EXPERIMENT_SETTINGS['sa'] = {'T': 1000}
DEFAULT_EXPERIMENT_SETTINGS['ga'] = {'max_iterations': 1000}


class ClassifierOptimization:
    def __init__(self, data):
        self.features, _, self.labels = data
        self.max_depth_range = (10, 100)
        self.min_samples_split_range = (2, 50)
        self.domain = self.create_domain()

    def create_domain(self):
        return [self.max_depth_range, self.min_samples_split_range]

    def compute_classification_error(self, solution):
        md, ms = solution
        clf = DecisionTreeClassifier(max_depth=md, min_samples_split=ms)
        scores = cross_val_score(clf, self.features, self.labels, cv=10)
        mean_score = scores.mean()
        return 1 - mean_score


def baseline_dt(data):
    features, _, labels = data
    clf = DecisionTreeClassifier()
    scores = cross_val_score(clf, features, labels, cv=10)
    mean_score = scores.mean()
    return mean_score


def plot_evaluation(df):
    sns.set(style="ticks")
    sns.lmplot("evaluations", "optimal_value", data=df, col='algo', hue='algo')


def compare_all(data, experiment_settings=DEFAULT_EXPERIMENT_SETTINGS):
    opt_problem = ClassifierOptimization(data)
    domain = opt_problem.domain
    rhc = hillclimb(domain=domain,
                    costf=opt_problem.compute_classification_error,
                    max_evaluations=experiment_settings['rhc']['evaluations'])
    rhc.set_index('evaluations', inplace=True)
    sa = simulated_annealing(domain=domain,
                             costf=opt_problem.compute_classification_error,
                             T=experiment_settings['sa']['T'])
    sa.set_index('temperature', inplace=True)
    sa.drop('cost', inplace=True, axis=1)
    ga = genetic_optimize(domain=domain,
                          costf=opt_problem.compute_classification_error,
                          maxiter=experiment_settings['ga']['generations'])
    ga.set_index('generations', inplace=True)
    ga.drop('population_size', inplace=True, axis=1)
    return rhc, sa, ga


def plot_optimal_values(rhc_df, sa_df, ga_df):
    f, ax = plt.subplots(2, 2, figsize=(10,8))
    rhc_df.plot(title='Hill Climber', ax=ax[0][0], legend=False, sharex=False)
    ax[0][0].set_ylabel("optimal value")
    sa_df.plot(title='Simulated Annealing', logx=True, ax=ax[0][1], legend=False, sharex=False)
    ax[0][1].set_ylabel("optimal value")
    ga_df.plot(title='Genetic Algorithm', ax=ax[1][0], legend=False, sharex=False)
    ax[1][0].set_ylabel("optimal value")
    plt.tight_layout()