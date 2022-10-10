#!/usr/bin/python
"""organizes flow of model in end-to-end pipeline.
"""

def pipeline(reviewer_pool, grants_pool, funding, report, round_number):

    # iterate over grants in grants pool, review each grant
    # all reviewers review all grants atm
    for grant in grants_pool.grants:
        grant.round_number = round_number
        reviewer_pool.review_grant(grant, funding)
        reviewer_pool.give_feedback()
        reviewer_pool.start_discussion(grant)
        grant.aggregate_score()
        report.update_report(grant)
        reviewer_pool.airdrop()
        # print("N reviewers", len(grant.reviewers))
    


if __name__ == "__main__":
    pass