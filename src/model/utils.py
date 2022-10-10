#!/usr/bin/python
import pandas as pd

def validate_inputs(reviewer_file, grant_file):

    reviewer_dataframe = pd.read_csv(reviewer_file)
    grant_dataframe = pd.read_csv(grant_file)

    for counter in range(len(reviewer_dataframe)):
        assert(reviewer_dataframe.iloc[counter].social_level >=0 and reviewer_dataframe.iloc[counter].social_level <=1), "validation fail: reviewer social_level"
        assert(reviewer_dataframe.iloc[counter].ability_level >=0 and reviewer_dataframe.iloc[counter].ability_level <=1), "validation fail: reviewer ability_level"
        assert(reviewer_dataframe.iloc[counter].recognition_level >=0 and reviewer_dataframe.iloc[counter].recognition_level <=1), "validation fail: reviewer recognition_level"
        assert(reviewer_dataframe.iloc[counter].engagement >=0 and reviewer_dataframe.iloc[counter].engagement <=1), "validation fail: reviewer engagement"
        assert(reviewer_dataframe.iloc[counter].satisfaction >=0 and reviewer_dataframe.iloc[counter].satisfaction <=1), "validation fail: reviewer satisfaction"

        
    for counter in range(len(grant_dataframe)):
        assert(grant_dataframe.iloc[counter].value >=0 and grant_dataframe.iloc[counter].value <=1), "validation fail: grant value"
        assert(grant_dataframe.iloc[counter].clarity >=0 and grant_dataframe.iloc[counter].clarity <=1), "validation fail: grant clarity"
        assert(grant_dataframe.iloc[counter].legitimacy >=0 or grant_dataframe.iloc[counter].legitimacy <=1), "validation fail: grant legitimacy"


def safe_increase(value, increment):
    """ensures values cannot escape the bounds 0-1    
    """
    if (value + increment >=0) and (value + increment <=1):
        return value+increment
    else:
        return value


def safe_decrease(value, decrement):
    """ensures values cannot escape the bounds 0-1    
    """
    if (value - decrement >=0) and (value - decrement <=1):
        return value-decrement
    else:
        return value



if __name__ == "__main__":
    pass