
#!/usr/bin/python
"""Skeleton model for rewards group.

Rewards group incentive model

"""

from classes import *
from pipeline import *
from utils import *


# define files
reviewer_file = "data/reviewers.csv"
grants_file = "data/grants.csv"
config_file = "src/model_config.yaml"

validate_inputs(reviewer_file, grants_file)

n_rounds = 5
report = Report(config_file)
reviewer_pool = ReviewerPool(reviewer_file, config_file)

for round_number in range(n_rounds):
    # create reviewer and grant pools from csv files    
    grants_pool = GrantPool(grants_file)
    funding = FundingPool(config_file)  
    # could move the file definitions above in here
    # and load different files each round
    pipeline(reviewer_pool, grants_pool, funding, report, round_number)


print(report.dataframe)
report.save_to_file()

if __name__ == "__main__":
    pass