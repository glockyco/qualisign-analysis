import os

import numpy as np
import pandas as pd
from pandas import DataFrame
from plotnine import ggplot, geom_boxplot, aes, ggtitle, theme_classic, theme, coord_cartesian, xlab, ylab

from qualisign.configuration import ENGINE, QUALITY_ATTRIBUTES, QMOOD_METRICS, MISC_METRICS, \
    FEATURE_NAMES


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
        result = metrics.melt(id_vars=["is_pattern_project"], var_name="metric")
        result["category"] = result["is_pattern_project"].map({True: "Pattern", False: "Non-Pattern"})

        return result


class QmoodMetricsData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        columns = [f"{metric}_avg" for metric in QMOOD_METRICS] + ["is_pattern_project"]

        data = self._data.read()
        metrics = data[columns].rename(columns={f"{column}_avg": name for column, name in FEATURE_NAMES.items()})
        result = metrics.melt(id_vars=["is_pattern_project"], var_name="metric")
        result["category"] = result["is_pattern_project"].map({True: "Pattern", False: "Non-Pattern"})

        return result


class MiscMetricsData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        columns = [f"{metric}_avg" for metric in MISC_METRICS] + ["is_pattern_project"]

        data = self._data.read()
        metrics = data[columns].rename(columns={f"{column}_avg": name for column, name in FEATURE_NAMES.items()})
        metrics["LOC"] = data["loc_sum"]

        result = metrics.melt(id_vars=["is_pattern_project"], var_name="metric")
        result["category"] = result["is_pattern_project"].map({True: "Pattern", False: "Non-Pattern"})

        return result


class QmoodQaBoxplot:
    def __init__(self, data: QmoodQaMetricsData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        metrics = self._data["metric"].unique()

        for metric in metrics:
            data = self._data[self._data["metric"] == metric]
            q75, q25 = np.percentile(data["value"], [98, 2])

            (
                ggplot(data, aes(x="category", y="value"))
                + geom_boxplot(outlier_shape="")
                + coord_cartesian(ylim=(q75 * 0.8, q25 * 1.2))
                #+ facet_wrap(facets="metric", scales="free", ncol=3)
                + ggtitle(metric)
                #+ ggtitle("QMOOD Quality Attributes")
                + xlab("Category")
                + ylab("Value")
                + theme_classic(base_size=28, base_family="Helvetica")
                #+ theme(subplots_adjust={"wspace": 0.25, "hspace": 0.2})
            ).save(f"{file_path}.{metric}.pdf", width=24, height=24)


class QmoodBoxplot:
    def __init__(self, data: QmoodMetricsData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        metrics = self._data["metric"].unique()

        for metric in metrics:
            data = self._data[self._data["metric"] == metric]
            q75, q25 = np.percentile(data["value"], [98, 2])

            (
                ggplot(data, aes(x="category", y="value"))
                + geom_boxplot(outlier_shape="")
                + coord_cartesian(ylim=(q75 * 0.8, q25 * 1.2))
                #+ facet_wrap(facets="metric", scales="free", ncol=3)
                + ggtitle(metric)
                #+ ggtitle("QMOOD Quality Attributes")
                + xlab("Category")
                + ylab("Value")
                + theme_classic(base_size=28, base_family="Helvetica")
                + theme(subplots_adjust={"wspace": 0.25, "hspace": 0.2})
            ).save(f"{file_path}.{metric}.pdf", width=24, height=24)


class MiscMetricsBoxplot:
    def __init__(self, data: MiscMetricsData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        metrics = self._data["metric"].unique()

        for metric in metrics:
            data = self._data[self._data["metric"] == metric]
            q75, q25 = np.percentile(data["value"], [98, 2])

            (
                ggplot(data, aes(x="category", y="value"))
                + geom_boxplot(outlier_shape="")
                + coord_cartesian(ylim=(q75 * 0.8, q25 * 1.2))
                #+ facet_wrap(facets="metric", scales="free", ncol=3)
                + ggtitle(metric)
                #+ ggtitle("QMOOD Quality Attributes")
                + xlab("Category")
                + ylab("Value")
                + theme_classic(base_size=28, base_family="Helvetica")
                + theme(subplots_adjust={"wspace": 0.25, "hspace": 0.2})
            ).save(f"{file_path}.{metric}.pdf", width=24, height=24)


if __name__ == "__main__":
    folder = "images/analysis/"

    QmoodQaBoxplot(QmoodQaMetricsData(ProjectData())).create(f"{folder}10_qmood_qa_boxplots.pdf")
    QmoodBoxplot(QmoodMetricsData(ProjectData())).create(f"{folder}12_qmood_boxplots.pdf")
    MiscMetricsBoxplot(MiscMetricsData(ProjectData())).create(f"{folder}14_misc_boxplots.pdf")
