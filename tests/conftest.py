
import pytest
import random
import numpy as np


@pytest.fixture()
def set_random_float_attributes():
    """generates random data for building instances of Reviewer class
    """
    
    n_attr = 5
    n_reviewers = 1000
    
    return run_set_random_float_attributes(n_attr, n_reviewers)

def run_set_random_float_attributes(n_attr, n_reviewers):
    return np.random.rand(n_attr, n_reviewers)


@pytest.fixture()
def set_random_int_attributes():
    """generates random data for building instances of Reviewer class
    """
    
    n_attr = 5
    n_reviewers = 1000
    
    return run_set_random_int_attributes(n_attr, n_reviewers)

def run_set_random_int_attributes(n_attr, n_reviewers):
    return np.random.randint(1,1000,size=(n_attr, n_reviewers))
    