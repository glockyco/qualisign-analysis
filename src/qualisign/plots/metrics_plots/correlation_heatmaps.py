import os
from typing import Union

import pandas as pd
import seaborn as sns
from heatmap import heatmap
from matplotlib import pyplot as plt
from pandas import DataFrame

from qualisign.configuration import ENGINE, FEATURES, FEATURE_NAMES


class ClassData:
    _view_name = "mv_clazzes_features"
    _csv_path = f"data/{_view_name}.csv"

    _data = None

    def read(self) -> DataFrame:
        if self._data is not None:
            return self._data

        if not os.path.exists(self._csv_path):
            self._data = pd.read_sql_table(self._view_name, ENGINE)
            self._data.to_csv(self._csv_path)
        else:
            self._data = pd.read_csv(self._csv_path)

        return self._data


class PackageData:
    _view_name = "mv_pakkages_features"
    _csv_path = f"data/{_view_name}.csv"

    _data = None

    def read(self) -> DataFrame:
        if self._data is not None:
            return self._data

        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
        else:
            data = pd.read_csv(self._csv_path)

        self._data = data.rename(columns={f"{column}_avg": column for column in FEATURES})
        self._data["loc"] = self._data["loc_sum"]

        return self._data


class ProjectData:
    _view_name = "mv_projects_features"
    _csv_path = f"data/{_view_name}.csv"

    _data = None

    def read(self) -> DataFrame:
        if self._data is not None:
            return self._data

        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
        else:
            data = pd.read_csv(self._csv_path)

        self._data = data.rename(columns={f"{column}_avg": column for column in FEATURES})
        self._data["loc"] = self._data["loc_sum"]

        return self._data


class MetricsCorrelationData:
    def __init__(self, data: Union[ClassData, PackageData, ProjectData]):
        self._data = data

    def read(self) -> DataFrame:
        data = self._data.read()
        metrics = data[FEATURES]
        correlations = metrics.corr("spearman")

        results = []

        for feature_1 in FEATURES:
            for feature_2 in FEATURES:
                result = correlations[feature_1][feature_2]
                feature_1_name = FEATURE_NAMES[feature_1]
                feature_2_name = FEATURE_NAMES[feature_2]
                results.append([feature_1_name, feature_2_name, result])

        data = DataFrame(results)
        data.columns = ["metric_1", "metric_2", "correlation"]

        return data


class MetricsCorrelationPlot:
    def __init__(self, data: MetricsCorrelationData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        plt.figure(figsize=(12, 11.7))

        plt.gcf().subplots_adjust(bottom=0.2, left=0.2)

        small_size = 16
        medium_size = 16
        bigger_size = 16

        plt.rc('font', size=small_size)  # controls default text sizes
        plt.rc('axes', titlesize=small_size)  # fontsize of the axes title
        plt.rc('axes', labelsize=medium_size)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=small_size)  # fontsize of the tick labels
        plt.rc('legend', fontsize=small_size)  # legend fontsize
        plt.rc('figure', titlesize=bigger_size)  # fontsize of the figure title

        heatmap(
            x=self._data["metric_1"],
            y=self._data["metric_2"],

            x_order=FEATURE_NAMES.values(),
            y_order=reversed(list(FEATURE_NAMES.values())),

            size=self._data["correlation"].abs(),
            size_range=[0, 1],
            size_scale=300,

            color=self._data["correlation"],
            color_range=[-1, 1],

            #palette=sns.diverging_palette(220, 20, n=256),
            palette=sns.color_palette("coolwarm", 256),

            #xlabel="Metric 1",
            #ylabel="Metric 2",
        )
        #sns.heatmap(self._data, annot=True, square=True)
        plt.savefig(file_path)


if __name__ == "__main__":
    folder = "images/statistics/"

    #MetricsCorrelationPlot(MetricsCorrelationData(ClassData())).create(f"{folder}06_class_metrics_correlations.pdf")
    #MetricsCorrelationPlot(MetricsCorrelationData(PackageData())).create(f"{folder}06_package_metrics_correlations.pdf")
    MetricsCorrelationPlot(MetricsCorrelationData(ProjectData())).create(f"{folder}06_project_metrics_correlations.pdf")
