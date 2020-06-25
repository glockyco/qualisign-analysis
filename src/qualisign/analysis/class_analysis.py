import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy import stats
from scipy.stats.stats import SpearmanrResult

from qualisign.configuration import CLASS_FEATURES_TABLE, ENGINE, QUALITY_ATTRIBUTES, DESIGN_PATTERNS, FEATURES


class ClassReader:
    def read_features(self) -> DataFrame:
        features = pd.read_sql_table(CLASS_FEATURES_TABLE, ENGINE)

        for pattern in DESIGN_PATTERNS:
            features[f"is_{pattern}"] = features[f"{pattern}_count"] > 0

        return features


class ClassAnalysis:
    def analyze(self, class_features: DataFrame) -> None:
        self.calculate_correlations(class_features)
        self.calculate_mann_whitney(class_features)
        self.create_boxplots(class_features)

    def calculate_correlations(self, class_features: DataFrame) -> None:
        correlations_count = pd.DataFrame()
        correlations_is = pd.DataFrame()

        for pattern in DESIGN_PATTERNS:
            class_features[f"is_{pattern}"] = class_features[f"{pattern}_count"] > 0

        for pattern in DESIGN_PATTERNS:
            pattern_correlations_count: Dict[str, SpearmanrResult] = {
                attribute: stats.spearmanr(
                    class_features[f"{pattern}_count"],
                    class_features[f"{attribute}"]
                ) for attribute in FEATURES
            }

            pattern_correlations_is: Dict[str, SpearmanrResult] = {
                attribute: stats.spearmanr(
                    class_features[f"is_{pattern}"],
                    class_features[f"{attribute}"]
                ) for attribute in FEATURES
            }

            results_count = {"pattern": pattern, **pattern_correlations_count}
            results_is = {"pattern": pattern, **pattern_correlations_is}

            correlations_count = correlations_count.append(results_count, ignore_index=True)
            correlations_is = correlations_is.append(results_is, ignore_index=True)

        correlations_count.set_index("pattern", inplace=True)
        correlations_is.set_index("pattern", inplace=True)

        # TODO: split business logic from "persistence"

        def spearmanr_result_to_string(result: SpearmanrResult) -> str:
            return f"{result.correlation:0.2f} ({result.pvalue:0.2f})"

        correlations_count.apply(np.vectorize(spearmanr_result_to_string)).to_csv("correlations_c_count.csv")
        correlations_is.apply(np.vectorize(spearmanr_result_to_string)).to_csv("correlations_c_is.csv")

    def calculate_mann_whitney(self, clazz_features: DataFrame) -> None:
        np_features = clazz_features[~clazz_features["is_pattern_clazz"]]
        p_features = clazz_features[clazz_features["is_pattern_clazz"]]

        results = pd.DataFrame()

        for feature in FEATURES:
            np_feature = np_features[f"{feature}"]
            p_feature = p_features[f"{feature}"]

            u, p = stats.mannwhitneyu(np_feature, p_feature)

            results = results.append({"feature": feature, "u": u, "p": p}, ignore_index=True)

        results.set_index("feature", inplace=True)

        results.to_csv("mann_whitney_c.csv")

    def create_boxplots(self, class_features: DataFrame) -> None:
        np_features = class_features[~class_features["is_pattern_clazz"]]
        p_features = class_features[class_features["is_pattern_clazz"]]

        sp_features = class_features[class_features["is_single_pattern_clazz"]]
        mp_features = class_features[class_features["is_multi_pattern_clazz"]]

        npnips_features = class_features[~class_features["is_pattern_clazz"] & ~class_features["is_in_pattern_project"]]
        npips_features = class_features[~class_features["is_pattern_clazz"] & class_features["is_in_pattern_project"]]
        npipp_features = class_features[~class_features["is_pattern_clazz"] & class_features["is_in_pattern_pakkage"]]

        features = [f"{attribute}" for attribute in QUALITY_ATTRIBUTES]

        fig_all, axs_all = plt.subplots(2, 3, figsize=(16, 10))

        index = 0
        for feature in features:
            row = index // 3
            col = index % 3
            index += 1

            data = [
                np_features[feature],
                p_features[feature],
                sp_features[feature],
                mp_features[feature],
                npnips_features[feature],
                npips_features[feature],
                npipp_features[feature],
            ]

            # All Features

            axs_all[row, col].set_title(f"{feature}")
            axs_all[row, col].boxplot(data, False, '', labels=["NP", "P", "SP", "MP", "NP-NIPS", "NP-IPS", "NP-IPP"])

            # Current Feature

            fig, ax = plt.subplots()

            ax.set_title(f"Classes - {feature}")
            ax.boxplot(data, False, '', labels=["NP", "P", "SP", "MP", "NP-NIPS", "NP-IPS", "NP-IPP"])

            fig.savefig(os.path.join("images", "classes", "boxplots", f"{feature}.png"))

        fig_all.suptitle("Classes")
        fig_all.savefig(os.path.join("images", f"_classes_boxplots_.png"))

        # TODO: collate plots into a single one
        # TODO: fix axes labels

        # TODO: split logic for plots and logic for correlations
        pass
