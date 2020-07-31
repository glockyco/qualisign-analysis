import math
from typing import List

import numpy as np
from mizani.transforms import trans_new, trans


def asinh_breaks(limits: List[float]) -> List[float]:
    limits = [int(round(limit)) for limit in limits]

    def br(r: List[float]) -> List[float]:
        lmin = int(round(math.log10(min(r))))
        lmax = int(round(math.log10(max(r))))
        lbreaks = range(lmin, lmax + 1, 1)
        breaks = [math.pow(10, b) for b in lbreaks]

        return breaks

    has_positive_limit = limits[1] > 0
    has_negative_limit = limits[0] < 0

    breaks = []
    positive_breaks = []
    negative_breaks = []

    if has_positive_limit:
        if min(limits) <= 0:
            limits += [1]

        positive_breaks = br([limit for limit in limits if limit > 0])

    if has_negative_limit:
        if max(limits) >= 0:
            limits += [-1]

        negative_breaks = [-b for b in br([-limit for limit in limits if limit < 0])]

    show_positive_breaks = len(negative_breaks) == 0 or len(positive_breaks) > 1
    show_negative_breaks = len(positive_breaks) == 0 or len(negative_breaks) > 1
    show_zero_break = not (show_positive_breaks and show_negative_breaks)

    if len(positive_breaks) > 5:
        step = int(len(positive_breaks) / 6) + 1
        positive_breaks = positive_breaks[::step]

    if show_positive_breaks:
        breaks += positive_breaks

    if show_negative_breaks:
        breaks += negative_breaks

    if show_zero_break:
        breaks += [0]

    breaks.sort()

    return breaks


def asinh_trans() -> trans:
    return trans_new("asinh", transform=np.arcsinh, inverse=np.sinh, breaks=asinh_breaks)


def asinh_labels(breaks: List[float]) -> List[str]:
    def asinh_label(br: float) -> str:
        br = int(round(br))

        if br == 0 or br == 1 or br == -1 or br == 10 or br == -10:
            return f"$\\mathdefault{{{int(br)}}}$"
        elif br < 0:
            exponent = int(round(math.log10(abs(br))))
            return f"$\\mathdefault{{-10^{{{exponent}}}}}$"
        else:
            exponent = int(round(math.log10(br)))
            return f"$\\mathdefault{{10^{{{exponent}}}}}$"

    return [asinh_label(br) for br in breaks]



