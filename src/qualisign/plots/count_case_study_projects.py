from mizani.formatters import comma_format
from pandas import DataFrame
from plotnine import geom_bar, ggplot, aes, ggtitle, xlab, ylab, scale_x_discrete, position_stack, geom_text, \
    scale_y_continuous, theme_classic, theme, element_text, position_dodge, geom_histogram


class CaseStudyAggregateCountData:
    def read(self) -> DataFrame:
        return DataFrame(data={
            #"category": [1, 2, 3, 5, 26, 52, 97, 100, 300, 537],
            "count": ["1"] * 5 + ["2"] * 5 + ["3"] * 9 + ["5"] * 2 + ["26"] + ["52"] + ["97"] + ["100"] + ["300"] + ["537"],
            #"count": [5, 5, 9, 2, 1, 1, 1, 1, 1, 1],
            #"percent": ["100%", "65.1%", "34.9%"],
        })


class CaseStudyAggregateCountPlot:
    def __init__(self, data: CaseStudyAggregateCountData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes(x="count", label="..count.."))
            + geom_bar(fill="#1e4f79")
            + geom_text(stat="count", va='bottom', size=24)
            + scale_x_discrete(limits=["1", "2", "3", "5", "26", "52", "97", "100", "300", "537"])
            + scale_y_continuous(breaks=[0, 5, 10], limits=[0, 10])
            + ggtitle("Case Study Sizes")
            + xlab("Number of Projects")
            + ylab("Number of Case Studies")
            + theme_classic(base_size=28, base_family="Helvetica")
            + theme(text=element_text(size=28))
        ).save(file_path, width=14, height=7)


if __name__ == "__main__":
    folder = "images/statistics/"

    CaseStudyAggregateCountPlot(CaseStudyAggregateCountData()).create(f"{folder}00_case_study_counts.pdf")
