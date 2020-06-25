import os

import pandas as pd
from pandas import DataFrame
from plotnine import ggplot, aes, ggtitle, xlab, ylab, theme_classic, geom_histogram, \
    facet_wrap, coord_cartesian

from qualisign.configuration import ENGINE, DESIGN_PATTERNS, DESIGN_PATTERN_NAMES


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


class PatternFractionData:
    def __init__(self, data: ProjectData):
        self._data = data

    def read(self) -> DataFrame:
        columns = [f"{pattern}_fraction" for pattern in DESIGN_PATTERNS]

        result = self._data.read()

        result = result[columns].rename(columns={f"{pattern}_fraction": name for pattern, name in DESIGN_PATTERN_NAMES.items()})
        result = result.melt()
        result = result[result["value"] != 0]
        result["variable"] = result["variable"].replace("Proxy2", "Proxy")

        return result


class PatternFractionDistributionsPlot:
    def __init__(self, data: PatternFractionData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes("value"))
            + geom_histogram(bins=100, fill="#1e4f79")
            + facet_wrap(facets="variable", ncol=3)
            #+ scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(self._data)) for v in l])
            + coord_cartesian()
            + ggtitle("Intensity of Design Pattern Use")
            + xlab("Percentage of Classes Participating in Design Pattern")
            + ylab("Number of Projects")
            + theme_classic(base_size=28, base_family="Helvetica")
            #+ theme(subplots_adjust={"wspace": 0.25, "hspace": 0.5})
        ).save(file_path, width=24, height=24)


if __name__ == "__main__":
    folder = "images/statistics/"

    PatternFractionDistributionsPlot(PatternFractionData(ProjectData())).create(f"{folder}8_pattern_distributions.png")
