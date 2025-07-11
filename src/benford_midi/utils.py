import numpy as np
from scipy.stats import uniform


def format_p(p):
    return "{:.3e}".format(p) if p < 0.001 else "{:.4f}".format(p)


def get_first_digit(x):
    """Get the first significant digit of a number"""
    x = np.asarray(x)
    mask = (x != 0) & ~np.isnan(x)  # Exclude zeros and NaNs
    x = np.abs(x[mask])
    first_digits = np.zeros_like(x, dtype=int)
    pos = x > 0
    first_digits[pos] = np.floor(x[pos] / 10 ** np.floor(np.log10(x[pos])))
    return first_digits


def get_significand(x):
    """Get the significand (mantissa) of a number in [1, 10)"""
    x = np.asarray(x)
    mask = (x != 0) & ~np.isnan(x)  # Exclude zeros and NaNs
    x = np.abs(x[mask])
    s = np.zeros_like(x)
    pos = x > 0
    s[pos] = 10 ** (np.log10(x[pos]) % 1)
    return s


def benford_first_digit_prob(d):
    """Benford's law probability for first digit"""
    return np.log10(1 + 1 / d)


def generate_benford_sample(n):
    """Generate n Benford-distributed numbers"""
    u = uniform.rvs(size=n)
    return 10**u


def z_transform(x, d, k=1):
    """Compute Z_d(X) transform for first k digits"""
    s = get_significand(x)
    c_d = d  # For first digit (k=1)
    if k > 1:
        pass
    return (
        (10 ** (k - 1) * s)
        * ((10 ** (k - 1) * s) >= c_d)
        * ((10 ** (k - 1) * s) < c_d + 1)
    )


def get_props(observed, expected):
    observed = np.asarray(observed, dtype=float)
    expected = np.asarray(expected, dtype=float)

    # Calculate proportions
    observed_props = observed / observed.sum()
    expected_props = expected / expected.sum()
    return observed_props, expected_props
