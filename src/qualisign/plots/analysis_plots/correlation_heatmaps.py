import os

import pandas as pd
import seaborn as sns
from heatmap import corrplot, heatmap
from matplotlib import pyplot as plt
from pandas import DataFrame

from qualisign.configuration import ENGINE, DESIGN_PATTERNS, QUALITY_ATTRIBUTES, QMOOD_METRICS, MISC_METRICS, \
    DESIGN_PATTERN_NAMES, QUALITY_ATTRIBUTE_NAMES, FEATURE_NAMES, QMOOD_METRICS_NAMES, MISC_METRICS_NAMES


class QmoodQaCorrelationData:
    _view_name = "mv_projects_features"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
        else:
            data = pd.read_csv(self._csv_path)

        pattern_columns = [f"{pattern}_fraction" for pattern in DESIGN_PATTERNS]
        metrics_columns = [f"{metric}_avg" for metric in QUALITY_ATTRIBUTES]
        columns = pattern_columns + metrics_columns

        data = data[columns]
        correlations = data.corr("spearman")

        results = []

        for pattern in DESIGN_PATTERNS:
            for metric in QUALITY_ATTRIBUTES:
                result = correlations[f"{pattern}_fraction"][f"{metric}_avg"]
                pattern_name = DESIGN_PATTERN_NAMES[pattern]
                metric_name = FEATURE_NAMES[metric]
                results.append([pattern_name, metric_name, result])

        data = DataFrame(results)
        data.columns = ["pattern", "metric", "correlation"]

        return data


class QmoodCorrelationData:
    _view_name = "mv_projects_features"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
        else:
            data = pd.read_csv(self._csv_path)

        pattern_columns = [f"{pattern}_fraction" for pattern in DESIGN_PATTERNS]
        metrics_columns = [f"{metric}_avg" for metric in QMOOD_METRICS]
        columns = pattern_columns + metrics_columns

        data = data[columns]
        correlations = data.corr("spearman")

        results = []

        for pattern in DESIGN_PATTERNS:
            for metric in QMOOD_METRICS:
                result = correlations[f"{pattern}_fraction"][f"{metric}_avg"]
                pattern_name = DESIGN_PATTERN_NAMES[pattern]
                metric_name = FEATURE_NAMES[metric]
                results.append([pattern_name, metric_name, result])

        data = DataFrame(results)
        data.columns = ["pattern", "metric", "correlation"]

        return data


class MiscMetricsCorrelationData:
    _view_name = "mv_projects_features"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
        else:
            data = pd.read_csv(self._csv_path)

        pattern_columns = [f"{pattern}_fraction" for pattern in DESIGN_PATTERNS]
        metrics_columns = [f"{metric}_avg" for metric in MISC_METRICS]
        columns = pattern_columns + metrics_columns

        data["loc_avg"] = data["loc_sum"]
        data = data[columns]
        correlations = data.corr("spearman")

        results = []

        for pattern in DESIGN_PATTERNS:
            for metric in MISC_METRICS:
                result = correlations[f"{pattern}_fraction"][f"{metric}_avg"]
                pattern_name = DESIGN_PATTERN_NAMES[pattern]
                metric_name = FEATURE_NAMES[metric]
                results.append([pattern_name, metric_name, result])

        data = DataFrame(results)
        data.columns = ["pattern", "metric", "correlation"]

        return data


class QmoodQaCorrelationPlot:
    def __init__(self, data: QmoodQaCorrelationData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        plt.figure(figsize=(15, 7.5))

        plt.gcf().subplots_adjust(bottom=0.4, left=0.2)

        small_size = 14
        medium_size = 16
        bigger_size = 18

        plt.rc('font', size=small_size)  # controls default text sizes
        plt.rc('axes', titlesize=small_size)  # fontsize of the axes title
        plt.rc('axes', labelsize=medium_size)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('legend', fontsize=small_size)  # legend fontsize
        plt.rc('figure', titlesize=bigger_size)  # fontsize of the figure title

        heatmap(
            x=self._data["pattern"],
            y=self._data["metric"],

            x_order=DESIGN_PATTERN_NAMES.values(),
            y_order=reversed(list(QUALITY_ATTRIBUTE_NAMES.values())),

            size=self._data["correlation"].abs(),
            size_range=[0, 1],
            size_scale=500,

            color=self._data["correlation"],
            color_range=[-1, 1],

            #palette=sns.diverging_palette(220, 20, n=256),
            palette=sns.color_palette("coolwarm", 256),

            xlabel="Design Pattern",
            ylabel="QMOOD Quality Attribute",
        )

        plt.savefig(file_path)


class QmoodCorrelationPlot:
    def __init__(self, data: QmoodCorrelationData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        plt.figure(figsize=(15, 12))

        plt.gcf().subplots_adjust(bottom=0.25)

        small_size = 14
        medium_size = 16
        bigger_size = 18

        plt.rc('font', size=small_size)  # controls default text sizes
        plt.rc('axes', titlesize=small_size)  # fontsize of the axes title
        plt.rc('axes', labelsize=medium_size)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('legend', fontsize=small_size)  # legend fontsize
        plt.rc('figure', titlesize=bigger_size)  # fontsize of the figure title

        heatmap(
            x=self._data["pattern"],
            y=self._data["metric"],

            x_order=DESIGN_PATTERN_NAMES.values(),
            y_order=reversed(list(QMOOD_METRICS_NAMES.values())),

            size=self._data["correlation"].abs(),
            size_range=[0, 1],
            size_scale=500,

            color=self._data["correlation"],
            color_range=[-1, 1],

            #palette=sns.diverging_palette(220, 20, n=256),
            palette=sns.color_palette("coolwarm", 256),

            xlabel="Design Pattern",
            ylabel="QMOOD Design Property",
        )

        plt.savefig(file_path)


class MiscMetricsCorrelationPlot:
    def __init__(self, data: MiscMetricsCorrelationData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        plt.figure(figsize=(15, 13))

        plt.gcf().subplots_adjust(bottom=0.25)

        small_size = 14
        medium_size = 16
        bigger_size = 18

        plt.rc('font', size=small_size)  # controls default text sizes
        plt.rc('axes', titlesize=small_size)  # fontsize of the axes title
        plt.rc('axes', labelsize=medium_size)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('legend', fontsize=small_size)  # legend fontsize
        plt.rc('figure', titlesize=bigger_size)  # fontsize of the figure title

        heatmap(
            x=self._data["pattern"],
            y=self._data["metric"],

            x_order=DESIGN_PATTERN_NAMES.values(),
            y_order=reversed(list(MISC_METRICS_NAMES.values())),

            size=self._data["correlation"].abs(),
            size_range=[0, 1],
            size_scale=500,

            color=self._data["correlation"],
            color_range=[-1, 1],

            #palette=sns.diverging_palette(220, 20, n=256),
            palette=sns.color_palette("coolwarm", 256),

            xlabel="Design Pattern",
            ylabel="C&K+ Metric",
        )

        plt.savefig(file_path)


if __name__ == "__main__":
    folder = "images/analysis/"

    QmoodQaCorrelationPlot(QmoodQaCorrelationData()).create(f"{folder}11_qmood_qa_correlations.png")
    QmoodCorrelationPlot(QmoodCorrelationData()).create(f"{folder}13_qmood_correlations.png")
    MiscMetricsCorrelationPlot(MiscMetricsCorrelationData()).create(f"{folder}15_misc_correlations.png")
