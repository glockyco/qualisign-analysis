import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy import stats
from scipy.stats.stats import SpearmanrResult

from qualisign.configuration import ENGINE, PACKAGE_FEATURES_TABLE, QUALITY_ATTRIBUTES, DESIGN_PATTERNS, FEATURES


class PackageReader:
    def read_features(self) -> DataFrame:
        return pd.read_sql_table(PACKAGE_FEATURES_TABLE, ENGINE)


class PackageAnalysis:
    def analyze(self, package_features: DataFrame) -> None:
        self.calculate_correlations(package_features)
        self.create_boxplots(package_features)

    def calculate_correlations(self, package_features: DataFrame) -> None:
        correlations = pd.DataFrame()

        for pattern in DESIGN_PATTERNS:
            pattern_correlations: Dict[str, SpearmanrResult] = {
                attribute: stats.spearmanr(
                    package_features[f"{pattern}_fraction"],
                    package_features[f"{attribute}_avg"]
                ) for attribute in FEATURES
            }

            results = {"pattern": pattern, **pattern_correlations}

            correlations = correlations.append(results, ignore_index=True)

        correlations.set_index("pattern", inplace=True)

        # TODO: split business logic from "persistence"

        def spearmanr_result_to_string(result: SpearmanrResult) -> str:
            return f"{result.correlation:0.2f} ({result.pvalue:0.2f})"

        correlations.apply(np.vectorize(spearmanr_result_to_string)).to_csv("correlations_p.csv")

    def create_boxplots(self, package_features: DataFrame) -> None:
        np_features = package_features[~package_features["is_pattern_pakkage"]]
        p_features = package_features[package_features["is_pattern_pakkage"]]

        np_nips_features = package_features[~package_features["is_pattern_pakkage"] & ~package_features["is_in_pattern_project"]]
        np_ips_features = package_features[~package_features["is_pattern_pakkage"] & package_features["is_in_pattern_project"]]

        features = [f"{attribute}_avg" for attribute in QUALITY_ATTRIBUTES]

        fig_all, axs_all = plt.subplots(2, 3, figsize=(16, 10))

        index = 0
        for feature in features:
            row = index // 3
            col = index % 3
            index += 1

            data = [
                np_features[feature],
                p_features[feature],
                np_nips_features[feature],
                np_ips_features[feature],
            ]

            # All Features

            axs_all[row, col].set_title(f"{feature}")
            axs_all[row, col].boxplot(data, False, '', labels=["NP", "P", "NP-NIPS", "NP-IPS"])

            # Current Feature

            fig, ax = plt.subplots()

            ax.set_title(f"Packages - {feature}")
            ax.boxplot(data, False, '', labels=["NP", "P", "NP-NIPS", "NP-IPS"])

            fig.savefig(os.path.join("images", "packages", "boxplots", f"{feature}.png"))

        fig_all.suptitle("Packages")
        fig_all.savefig(os.path.join("images", f"_packages_boxplots_.png"))

        # TODO: collate plots into a single one
        # TODO: fix axes labels

        # TODO: split logic for plots and logic for correlations
        pass
