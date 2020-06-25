from mizani.formatters import comma_format
from pandas import DataFrame
from plotnine import geom_bar, ggplot, aes, ggtitle, xlab, ylab, scale_x_discrete, position_stack, geom_text, \
    scale_y_continuous, theme_classic, theme, element_text, position_dodge


class ProjectCountData:
    def read(self) -> DataFrame:
        return DataFrame(data={
            "category": ["All", "Non-Pattern", "Pattern"],
            "count": [89621, 58323, 31298],
            "percent": ["100%", "65.1%", "34.9%"],
        })


class PackageCountData:
    def read(self) -> DataFrame:
        return DataFrame(data={
            "category": ["All", "Non-Pattern", "Pattern"],
            "count": [321046, 229031, 92015],
            "percent": ["100%", "71.3%", "28.7%"],
        })


class ClassCountData:
    def read(self) -> DataFrame:
        return DataFrame(data={
            "category": ["All", "Non-Pattern", "Pattern", "Single-Pattern", "Multi-Pattern"],
            "count": [2969494, 2630717, 338777, 241119, 97658],
            "percent": ["100%", "88.6%", "11.4%", "8.1%", "3.3%"],
        })


class ProjectCountPlot:
    def __init__(self, data: ProjectCountData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes(x="category", y="count", label="percent"))
            + geom_bar(stat="identity", fill="#1e4f79")
            + geom_text(va='bottom', size=18)
            + scale_x_discrete(limits=self._data["category"])
            + scale_y_continuous(labels=comma_format(), expand=[0.1, 0])
            + ggtitle("Projects per Category")
            + xlab("Category")
            + ylab("Number of Projects")
            + theme_classic(base_size=24, base_family="Helvetica")
            + theme(axis_text_x=element_text(rotation=45, ha="right"), aspect_ratio=1)
        ).save(file_path)


class PackageCountPlot:
    def __init__(self, data: PackageCountData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes(x="category", y="count", label="percent"))
            + geom_bar(stat="identity", fill="#1e4f79")
            + geom_text(va='bottom', size=18)
            + scale_x_discrete(limits=self._data["category"])
            + scale_y_continuous(labels=comma_format(), expand=[0.1, 0])
            + ggtitle("Packages per Category")
            + xlab("Category")
            + ylab("Number of Packages")
            + theme_classic(base_size=24, base_family="Helvetica")
            + theme(axis_text_x=element_text(rotation=45, ha="right"), aspect_ratio=1)
        ).save(file_path)


class ClassCountPlot:
    def __init__(self, data: ClassCountData):
        self._data = data.read()

    def create(self, file_path: str) -> None:
        (
            ggplot(self._data, aes(x="category", y="count", label="percent"))
            + geom_bar(stat="identity", fill="#1e4f79")
            + geom_text(va='bottom', size=18)
            + scale_x_discrete(limits=self._data["category"])
            + scale_y_continuous(labels=comma_format(), expand=[0.1, 0])
            + ggtitle("Classes per Category")
            + xlab("Category")
            + ylab("Number of Classes")
            + theme_classic(base_size=24, base_family="Helvetica")
            + theme(axis_text_x=element_text(rotation=45, ha="right"), aspect_ratio=1)
        ).save(file_path)


if __name__ == "__main__":
    folder = "images/statistics/"

    ProjectCountPlot(ProjectCountData()).create(f"{folder}1_project_counts.png")
    PackageCountPlot(PackageCountData()).create(f"{folder}1_package_counts.png")
    ClassCountPlot(ClassCountData()).create(f"{folder}1_class_counts.png")
