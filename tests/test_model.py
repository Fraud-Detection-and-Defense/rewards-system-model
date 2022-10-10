#!/usr/bin/python
import random
import matplotlib.pyplot as plt
import numpy as np
import pytest
from  src.model.utils import *
from src.model.classes import Reviewer


def test_build_reviewer_with_floats(set_random_float_attributes):
    """
    For N random floats can we reliably build instances of the 
    Reviewer class?
    """
    for i in range(1000):
        reviewer = Reviewer(
            config_file = "src/model_config.yaml",
            reviewer_number = i,
            social_level = set_random_float_attributes[0,i],
            ability_level = set_random_float_attributes[1,i],
            recognition_level = set_random_float_attributes[2,i],
            engagement = set_random_float_attributes[3,i],
            satisfaction = set_random_float_attributes[4,i]
        )   

    return


@pytest.mark.xfail()
def test_build_reviewer_with_ints(set_random_int_attributes):
    """
    For N random integers does reviewer-building reliably fail?
    (reviewer attributes should take floats only)
    """
    for i in range(1000):
        reviewer = Reviewer(
            reviewer_number = i,
            social_level = set_random_int_attributes[0,i],
            ability_level = set_random_int_attributes[1,i],
            recognition_level = set_random_int_attributes[2,i],
            engagement = set_random_int_attributes[3,i],
            satisfaction = set_random_int_attributes[4,i]
        )   

    return

if __name__ == "__main__":
    pass