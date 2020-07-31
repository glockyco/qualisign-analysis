import os

import pandas as pd
from mizani.formatters import comma_format
from pandas import DataFrame
from plotnine import geom_bar, ggplot, aes, ggtitle, xlab, ylab, scale_x_discrete, geom_text, \
    scale_y_continuous, theme_classic, theme, element_text

from qualisign.configuration import ENGINE


class PatternCountData:
    _view_name = "mv__plot_pattern_counts"
    _csv_path = f"data/{_view_name}.csv"

    def read(self) -> DataFrame:
        if not os.path.exists(self._csv_path):
            data = pd.read_sql_table(self._view_name, ENGINE)
            data.to_csv(self._csv_path)
            return data

        return pd.read_csv(self._csv_path)


class PatternCountPlot:
    def __init__(self, data: PatternCountData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes(x="pattern", y="count", label="fraction"))
            + geom_bar(stat="identity", fill="#1e4f79")
            + geom_text(va='bottom', size=24, format_string='{:.1%}')
            + scale_x_discrete(limits=self._data["pattern"])
            + scale_y_continuous(labels=comma_format(), expand=[0.1, 0])
            + ggtitle("Design Pattern Counts")
            + xlab("Design Pattern")
            + ylab("Count")
            + theme_classic(base_size=32, base_family="Helvetica")
            + theme(text=element_text(size=32), axis_text_x=element_text(rotation=45, ha="right"))
        ).save(file_path, width=24, height=8)


if __name__ == "__main__":
    folder = "images/statistics/"

    PatternCountPlot(PatternCountData()).create(f"{folder}07_pattern_counts.pdf")
