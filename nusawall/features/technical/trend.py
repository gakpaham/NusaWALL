def simple_trend(values):
    return float(sum(values[-3:]) / max(len(values[-3:]), 1))
