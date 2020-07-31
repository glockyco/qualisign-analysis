import os

import pandas as pd
from mizani.formatters import comma_format
from pandas import DataFrame
from plotnine import ggplot, aes, ggtitle, xlab, ylab, theme_classic, theme, geom_histogram, \
    scale_x_continuous, element_text, facet_grid, scale_y_continuous

from qualisign.configuration import ENGINE
from qualisign.utils.asinh_trans import asinh_trans, asinh_labels


class ProjectSizeData:
    _view_name = "mv__plot_project_sizes"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
            return data

        return pd.read_csv(self._csv_path)


class PackageSizeData:
    _view_name = "mv__plot_pakkage_sizes"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
            return data

        return pd.read_csv(self._csv_path)


class ClassSizeData:
    _view_name = "mv__plot_clazz_sizes"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
            return data

        return pd.read_csv(self._csv_path)


class ProjectSizesPlot:
    def __init__(self, data: ProjectSizeData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("loc"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_grid(facets="category ~ .", scales='free_y')
            + scale_x_continuous(trans=asinh_trans(), labels=asinh_labels)
            + scale_y_continuous(labels=comma_format())
            #+ scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(self._data)) for v in l])
            + ggtitle("Project Sizes")
            + xlab("Lines of Code")
            + ylab("Number of Projects")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), subplots_adjust={"hspace": 0.1})
        ).save(file_path, width=8, height=18)


class PackageSizesPlot:
    def __init__(self, data: PackageSizeData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("loc"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_grid(facets="category ~ .", scales='free_y')
            + scale_x_continuous(trans=asinh_trans(), labels=asinh_labels)
            + scale_y_continuous(labels=comma_format())
            #+ scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(self._data)) for v in l])
            + ggtitle("Package Sizes")
            + xlab("Lines of Code")
            + ylab("Number of Packages")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), subplots_adjust={"hspace": 0.1})
        ).save(file_path, width=8, height=18)


class ClassSizesPlot:
    def __init__(self, data: ClassSizeData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("loc"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_grid(facets="category ~ .", scales='free_y')
            + scale_x_continuous(trans=asinh_trans(), labels=asinh_labels)
            + scale_y_continuous(labels=comma_format())
            #+ scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(self._data)) for v in l])
            + ggtitle("Class Sizes")
            + xlab("Lines of Code")
            + ylab("Number of Classes")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), subplots_adjust={"hspace": 0.1})
        ).save(file_path, width=8, height=18)


if __name__ == "__main__":
    folder = "images/statistics/"

    ProjectSizesPlot(ProjectSizeData()).create(f"{folder}02_project_sizes.pdf")
    PackageSizesPlot(PackageSizeData()).create(f"{folder}02_package_sizes.pdf")
    ClassSizesPlot(ClassSizeData()).create(f"{folder}02_class_sizes.pdf")
