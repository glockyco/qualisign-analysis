import os

import pandas as pd
from mizani.formatters import comma_format
from pandas import DataFrame
from plotnine import ggplot, aes, ggtitle, xlab, ylab, scale_y_continuous, theme_classic, theme, geom_histogram, \
    scale_x_continuous, facet_wrap, element_text

from qualisign.configuration import ENGINE, QUALITY_ATTRIBUTES, QMOOD_METRICS, MISC_METRICS, FEATURE_NAMES
from qualisign.utils.asinh_trans import asinh_trans, asinh_labels


class ProjectData:
    _view_name = "mv_projects_features"
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


class QmoodQaMetricsData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        columns = [f"{metric}_avg" for metric in QUALITY_ATTRIBUTES] + ["is_pattern_project"]

        data = self._data.read()
        metrics = data[columns].rename(columns={f"{column}_avg": name for column, name in FEATURE_NAMES.items()})
        result = metrics.melt(["is_pattern_project"])

        return result


class QmoodMetricsData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        columns = [f"{metric}_avg" for metric in QMOOD_METRICS] + ["is_pattern_project"]

        data = self._data.read()
        metrics = data[columns].rename(columns={f"{column}_avg": name for column, name in FEATURE_NAMES.items()})
        result = metrics.melt(["is_pattern_project"])

        return result


class MiscMetricsData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        columns = [f"{metric}_avg" for metric in MISC_METRICS] + ["is_pattern_project"]

        data = self._data.read()
        metrics = data[columns].rename(columns={f"{column}_avg": name for column, name in FEATURE_NAMES.items()})
        metrics["LOC"] = data["loc_sum"]

        result = metrics.melt(["is_pattern_project"])

        return result


class QmoodQaMetricsDistributionsPlot:
    def __init__(self, data: QmoodQaMetricsData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("value"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_wrap(facets="variable", scales="free", ncol=3)
            + scale_x_continuous(trans=asinh_trans(), labels=asinh_labels)
            + scale_y_continuous(labels=comma_format())
            + ggtitle("Distributions of QMOOD Quality Attributes")
            + xlab("Quality Attribute Value")
            + ylab("Number of Projects")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), subplots_adjust={"wspace": 0.35, "hspace": 0.35})
        ).save(file_path, width=24, height=12)


class QmoodMetricsDistributionsPlot:
    def __init__(self, data: QmoodMetricsData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("value"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_wrap(facets="variable", scales="free", ncol=3)
            + scale_x_continuous(trans=asinh_trans(), labels=asinh_labels)
            + scale_y_continuous(labels=comma_format())
            + ggtitle("Distributions of QMOOD Design Properties")
            + xlab("Design Property Value")
            + ylab("Number of Projects")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), subplots_adjust={"wspace": 0.35, "hspace": 0.35})
        ).save(file_path, width=24, height=24)


class MiscMetricsDistributionsPlot:
    def __init__(self, data: MiscMetricsData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("value"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_wrap(facets="variable", scales="free", ncol=3)
            + scale_x_continuous(trans=asinh_trans(), labels=asinh_labels)
            + scale_y_continuous(labels=comma_format())
            + ggtitle("Distributions of C&K+ Metrics")
            + xlab("Metric Value")
            + ylab("Number of Projects")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), subplots_adjust={"wspace": 0.35, "hspace": 0.35})
        ).save(file_path, width=24, height=24)


if __name__ == "__main__":
    folder = "images/statistics/"

    QmoodQaMetricsDistributionsPlot(QmoodQaMetricsData(ProjectData())).create(f"{folder}03_qmood_qa_distributions.pdf")
    QmoodMetricsDistributionsPlot(QmoodMetricsData(ProjectData())).create(f"{folder}04_qmood_distributions.pdf")
    MiscMetricsDistributionsPlot(MiscMetricsData(ProjectData())).create(f"{folder}05_misc_distributions.pdf")
