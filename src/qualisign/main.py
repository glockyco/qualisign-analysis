from qualisign.analysis.class_analysis import ClassReader, ClassAnalysis
from qualisign.analysis.package_analysis import PackageReader, PackageAnalysis
from qualisign.analysis.project_analysis import ProjectAnalysis, ProjectReader


def analyze_projects() -> None:
    reader = ProjectReader()
    features = reader.read_features()
    analysis = ProjectAnalysis()
    analysis.analyze(features)

    # project_features.to_csv(os.path.join("data", "mv_projects_features.csv"))


def analyze_packages() -> None:
    reader = PackageReader()
    features = reader.read_features()
    analysis = PackageAnalysis()
    analysis.analyze(features)

    # project_features.to_csv(os.path.join("data", "mv_projects_features.csv"))


def analyze_classes() -> None:
    reader = ClassReader()
    features = reader.read_features()
    analysis = ClassAnalysis()
    analysis.analyze(features)

    # project_features.to_csv(os.path.join("data", "mv_projects_features.csv"))


if __name__ == "__main__":
    analyze_projects()
    analyze_packages()
    analyze_classes()

    # @TODO: create plots from the ./plots directory.
