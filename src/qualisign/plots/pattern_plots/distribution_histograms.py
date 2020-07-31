import os

import pandas as pd
from mizani.formatters import comma_format
from pandas import DataFrame
from plotnine import ggplot, aes, ggtitle, xlab, ylab, theme_classic, geom_histogram, \
    facet_wrap, theme, element_text, scale_y_continuous, xlim, scale_x_continuous

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
            + facet_wrap(facets="variable", scales="free", ncol=3)
            + xlim(0, 1)
            + scale_y_continuous(labels=comma_format())
            + ggtitle("Intensity of Design Pattern Use")
            + xlab("Percentage of Classes Participating in Design Pattern")
            + ylab("Number of Projects")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(
                text=element_text(size=32),
                axis_title_y=element_text(margin={"r": 40}),
                subplots_adjust={"wspace": 0.3, "hspace": 0.5})
        ).save(file_path, width=24, height=24)


if __name__ == "__main__":
    folder = "images/statistics/"

    PatternFractionDistributionsPlot(PatternFractionData(ProjectData())).create(f"{folder}08_pattern_distributions.pdf")
