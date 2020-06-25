from plotnine import geom_histogram, ggplot, aes, scale_x_log10, scale_y_continuous, xlab, ylab, facet_grid

from qualisign.analysis.class_analysis import ClassReader
from qualisign.analysis.package_analysis import PackageReader
from qualisign.analysis.project_analysis import ProjectReader

if __name__ == "__main__":

    project_reader = ProjectReader()
    project_features = project_reader.read_features()

    print("projects loaded!")

    package_reader = PackageReader()
    package_features = package_reader.read_features()

    print("packages loaded!")

    class_reader = ClassReader()
    class_features = class_reader.read_features()

    print("classes loaded!")

    (
        ggplot(project_features, aes('loc_sum'))
        + geom_histogram(bins=100)
        + facet_grid('is_pattern_project ~ .')
        + scale_x_log10(breaks=[1, 10, 100, 1000, 10000, 100000, 1000000, 10000000])
        + scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(project_features)) for v in l])
        + xlab("Lines of Code")
        + ylab("Percent of Projects")
    ).save('projects_histogram.png')

    print("projects drawn!")

    (
        ggplot(package_features, aes('loc_sum'))
        + geom_histogram(bins=100)
        + facet_grid('is_pattern_pakkage ~ .')
        + scale_x_log10(breaks=[1, 10, 100, 1000, 10000, 100000, 1000000, 10000000])
        + scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(package_features)) for v in l])
        + xlab("Lines of Code")
        + ylab("Percent of Packages")
    ).save("packages_histogram.png")

    print("packages drawn!")

    (
            ggplot(class_features, aes('loc'))
            + geom_histogram(bins=100)
            + facet_grid('is_pattern_clazz ~ .')
            + scale_x_log10(breaks=[1, 10, 100, 1000, 10000, 100000, 1000000, 10000000])
            + scale_y_continuous(labels=lambda l: ["%.2f%%" % (v * 100 / len(class_features)) for v in l])
            + xlab("Lines of Code")
            + ylab("Percent of Classes")
    ).save("classes_histogram.png")

    print("classes drawn!")


