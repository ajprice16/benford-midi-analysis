import pytest
from benford_midi.analysis import BenfordTests

def test_benford_tests_initialization():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    assert tests.n == len(data)
    assert tests.first_digits is not None
    assert tests.significands is not None

def test_pearson_chi2():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    chi2_stat, p_value = tests.pearson_chi2()
    assert p_value >= 0  # p-value should be non-negative

def test_kolmogorov_smirnov():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    ks_stat, p_value = tests.kolmogorov_smirnov()
    assert p_value >= 0  # p-value should be non-negative

def test_hotelling_q():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    q_stat, p_value = tests.hotelling_q(B=100)
    assert p_value >= 0  # p-value should be non-negative

def test_sup_norm_m():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    m_stat, p_value = tests.sup_norm_m(B=100)
    assert p_value >= 0  # p-value should be non-negative

def test_min_p_value_g():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    g_stat, p_value = tests.min_p_value_g(B=100)
    assert p_value >= 0  # p-value should be non-negative

def test_combined_test():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    fisher_stat, p_value = tests.combined_test(B=100)
    assert p_value >= 0  # p-value should be non-negative

def test_z_stat():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    z_stat = tests.zStat()
    assert z_stat >= 0  # z-stat should be non-negative

def test_mad():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    mad_value = tests.MAD()
    assert mad_value >= 0  # MAD should be non-negative

def test_ned():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    ned_value = tests.NED()
    assert ned_value >= 0  # NED should be non-negative

def test_return_observed_props():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    tests = BenfordTests(data)
    observed_props = tests.return_observed_props()
    assert observed_props is not None  # Should return observed proportions