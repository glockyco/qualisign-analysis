import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from scipy import stats
from scipy.stats.stats import SpearmanrResult

from qualisign.configuration import ENGINE, PROJECT_FEATURES_TABLE, DESIGN_PATTERNS, QUALITY_ATTRIBUTES, FEATURES


class ProjectReader:
    def read_features(self) -> DataFrame:
        return pd.read_sql_table(PROJECT_FEATURES_TABLE, ENGINE)


class ProjectAnalysis:
    def analyze(self, project_features: DataFrame) -> None:
        self.calculate_correlations(project_features)
        self.calculate_mann_whitney(project_features)
        self.create_scatterplots(project_features)
        self.create_boxplots(project_features)
        #self.create_pairplots(project_features)

    def calculate_correlations(self, project_features: DataFrame) -> None:
        correlations = pd.DataFrame()

        for pattern in DESIGN_PATTERNS:
            pattern_correlations: Dict[str, SpearmanrResult] = {
                attribute: stats.spearmanr(
                    project_features[f"{pattern}_fraction"],
                    project_features[f"{attribute}_avg"]
                ) for attribute in FEATURES
            }

            pattern_correlations.update({"loc_sum": stats.spearmanr(project_features[f"{pattern}_fraction"], project_features["loc_sum"])})

            results = {"pattern": pattern, **pattern_correlations}

            correlations = correlations.append(results, ignore_index=True)

        correlations.set_index("pattern", inplace=True)

        # TODO: split business logic from "persistence"

        def spearmanr_result_to_string(result: SpearmanrResult) -> str:
            return f"{result.correlation:0.2f} ({result.pvalue:0.2f})"

        correlations.apply(np.vectorize(spearmanr_result_to_string)).to_csv("correlations_s.csv")

    def calculate_mann_whitney(self, project_features: DataFrame) -> None:
        np_features = project_features[~project_features["is_pattern_project"]]
        p_features = project_features[project_features["is_pattern_project"]]

        results = pd.DataFrame()

        for feature in FEATURES:
            np_feature = np_features[f"{feature}_avg"]
            p_feature = p_features[f"{feature}_avg"]

            u, p = stats.mannwhitneyu(np_feature, p_feature)

            results = results.append({"feature": feature, "u": u, "p": p}, ignore_index=True)

        results.set_index("feature", inplace=True)

        results.to_csv("mann_whitney_s.csv")

    def create_pairplots(self, project_features: DataFrame):
        attributes = [f"{attribute}_avg" for attribute in QUALITY_ATTRIBUTES]
        patterns = [f"{pattern}_fraction" for pattern in DESIGN_PATTERNS]

        columns = ["is_pattern_project"] + attributes + patterns

        data = project_features[columns]

        sns.pairplot(data, hue="is_pattern_project")

    def create_scatterplots(self, project_features: DataFrame):
        features = [f"{attribute}_avg" for attribute in QUALITY_ATTRIBUTES]

        fig_all, axs_all = plt.subplots(2, 3, figsize=(160, 100))

        index = 0
        for feature in features:
            row = index // 3
            col = index % 3
            index += 1

            # All Features

            # axs_all[row, col].set_title(f"adapter vs. {feature}")

            axs_all[row, col].set_xlabel("adapter_fraction")
            axs_all[row, col].set_ylabel(feature)
            axs_all[row, col].scatter(project_features["adapter_fraction"], project_features[feature], 0.1)

            # Current Feature

            fig, ax = plt.subplots()

            ax.set_title(f"Projects - adapter_fraction vs. {feature}")

            ax.set_xlabel("adapter")
            ax.set_ylabel(feature)
            ax.scatter(project_features["adapter_fraction"], project_features[feature], 0.1)

            fig.savefig(os.path.join("images", "projects", "scatterplots", f"adapter_{feature}.png"))

        fig_all.suptitle("Projects")
        fig_all.savefig(os.path.join("images", "projects", "scatterplots", f"_adapter_all_.png"))

    def create_boxplots(self, project_features: DataFrame) -> None:
        np_features = project_features[~project_features["is_pattern_project"]]
        p_features = project_features[project_features["is_pattern_project"]]

        features = [f"{attribute}_avg" for attribute in QUALITY_ATTRIBUTES]

        fig_all, axs_all = plt.subplots(2, 3, figsize=(16, 10))

        index = 0
        for feature in features:
            row = index // 3
            col = index % 3
            index += 1

            data = [np_features[feature], p_features[feature]]

            # All Features

            axs_all[row, col].set_title(f"{feature}")
            axs_all[row, col].boxplot(data, False, '', labels=["NP", "P"])

            # Current Feature

            fig, ax = plt.subplots()

            ax.set_title(f"Projects - {feature}")
            ax.boxplot(data, False, '', labels=["NP", "P"])

            fig.savefig(os.path.join("images", "projects", "boxplots", f"{feature}.png"))

        fig_all.suptitle("Projects")
        fig_all.savefig(os.path.join("images", f"_projects_boxplots_.png"))

        # TODO: collate plots into a single one
        # TODO: fix axes labels

        # TODO: split logic for plots and logic for correlations
        pass
