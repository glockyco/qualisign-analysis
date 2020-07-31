import os

import pandas as pd
import seaborn as sns
from heatmap import heatmap
from matplotlib import pyplot as plt
from pandas import DataFrame

from qualisign.configuration import ENGINE, FEATURES, FEATURE_NAMES, DESIGN_PATTERNS, DESIGN_PATTERN_NAMES


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

        self._data = data.rename(columns={f"{column}_fraction": column for column in DESIGN_PATTERNS})

        return self._data


class PatternCorrelationData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        data = self._data.read()
        patterns = data[DESIGN_PATTERN_NAMES]
        correlations = patterns.corr("spearman")

        results = []

        for pattern_1 in DESIGN_PATTERNS:
            for pattern_2 in DESIGN_PATTERNS:
                result = correlations[pattern_1][pattern_2]
                pattern_1_name = DESIGN_PATTERN_NAMES[pattern_1]
                pattern_2_name = DESIGN_PATTERN_NAMES[pattern_2]
                results.append([pattern_1_name, pattern_2_name, result])

        data = DataFrame(results)
        data.columns = ["pattern_1", "pattern_2", "correlation"]

        return data


class PatternCorrelationPlot:
    def __init__(self, data: PatternCorrelationData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        plt.figure(figsize=(12, 11.5))

        plt.gcf().subplots_adjust(bottom=0.25, left=0.25)

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
            x=self._data["pattern_1"],
            y=self._data["pattern_2"],

            x_order=DESIGN_PATTERN_NAMES.values(),
            y_order=reversed(list(DESIGN_PATTERN_NAMES.values())),

            size=self._data["correlation"].abs(),
            size_range=[0, 1],
            size_scale=900,

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

    PatternCorrelationPlot(PatternCorrelationData(ProjectData())).create(f"{folder}09_project_patterns_correlations.pdf")
