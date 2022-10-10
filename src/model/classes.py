#!/usr/bin/python
"""Classes to be used in agent-based model.

Includes:
- Reviewer
- Pool
- Grant

"""

import yaml
from random import sample, choice, randint, random
import operator
import pandas as pd
from utils import *

class Reviewer():

    def __init__(self, config_file, reviewer_number, social_level,
                ability_level, recognition_level,
                engagement, satisfaction):
        self.config_file = config_file
        self.social_level = social_level
        self.ability_level = ability_level
        self.recognition_level = recognition_level
        self.engagement = engagement
        self.discussion_probability = sum([self.ability_level, self.social_level, self.recognition_level,self.engagement])/4
        self.satisfaction = satisfaction
        self.balance = 0
        self.poaps = 0
        self.trust_level = self.get_trust_level()
        self.reviewer_number = reviewer_number
        self.get_fee(self.config_file)
    

    def get_trust_level(self):

        attributes = [self.social_level, 
        self.ability_level,
        self.recognition_level, 
        self.engagement]

        mean_score = sum(attributes)/len(attributes)
        
        if mean_score <= 0.3:
            return 1
        elif mean_score <= 0.6:
            return 2
        else:
            return 3
        return 


    
    def get_fee(self, config_file):

        with open(config_file, "r") as ymlfile:
            inputs = yaml.load(ymlfile, Loader=yaml.FullLoader)

        if self.trust_level == 1:
            self.fee = inputs["config"]["L1_reviewer_fee"]
        if self.trust_level == 2:
            self.fee = inputs["config"]["L2_reviewer_fee"]
        if self.trust_level == 3:
            self.fee = inputs["config"]["L3_reviewer_fee"]


    def make_decision(self, grant, funding):
        """
        some function operating on grant and reviewer attributes
        and returning Boolean decision
        """

        # decision =  mean of (1-difficulty) and ability
        # is it < threshold? if so review correctly

        leniency = 0.5 # tweak this to 

        if ((1-grant.difficulty) + self.ability_level)/2 < leniency:
            self.decision = grant.true_outcome
        else:
            self.decision = 1-grant.true_outcome       

        grant.reviewer_scores.append(self.decision)
        funding.balance -= self.fee
        self.balance = safe_increase(self.fee, 0.1)
        self.satisfaction = safe_increase(self.satisfaction, 0.1)

        return 

      


class ReviewerPool():

    def __init__(self, reviewer_file, config_file):

        reviewers = []

        reviewer_dataframe = pd.read_csv(reviewer_file)
        for counter in range(len(reviewer_dataframe)):
            reviewer_number = reviewer_dataframe.iloc[counter].reviewer_number
            social_level = reviewer_dataframe.iloc[counter].social_level
            ability_level = reviewer_dataframe.iloc[counter].ability_level
            recognition_level = reviewer_dataframe.iloc[counter].recognition_level
            engagement = reviewer_dataframe.iloc[counter].engagement
            satisfaction = reviewer_dataframe.iloc[counter].satisfaction
            
            reviewer = Reviewer(config_file, reviewer_number, social_level, ability_level, recognition_level, engagement, satisfaction)
            reviewers.append(reviewer)

        self.reviewers = reviewers


    def review_grant(self, grant, funding):
        """
        iterates over all reviewers in pool and
        triggers a decision on the given grant
        """

        reviewers = sample(self.reviewers, 3)
        # random selection of 3 reviewers review a grant
        for reviewer in reviewers:
            
            if (((grant.value + grant.clarity)/2) < reviewer.ability_level):
                reviewer = sample(self.reviewers,1)[0]
            else:
                print(f"cannot find 3 reviewers qualified to review grant {grant.grant_number}. Grant marked unsafe.")
                grant.unsafe = 1

            reviewer.make_decision(grant, funding)
            reviewer.ability_level  = safe_increase(reviewer.ability_level, 0.1)
            grant.reviewers.append(reviewer)
            

    def give_feedback(self):
        """
        A round of feedback involves taking each reviewer in the pool and a random
        pair of peers. For each combination of reviewers in the group
        the one with the higher trust level can give feedback to the
        other, increasing the lower trust reviewer's ability level by 0.2
        """

        for i in range(0,len(self.reviewers)):
            feedback_giver = self.reviewers[i]
            others = self.reviewers[:i] + self.reviewers[i+1 :]
            group = sample(others, 2)
            
            for feedback_receiver in group:
                #print("giving feedback")
                if feedback_receiver.trust_level < feedback_giver.trust_level:
                    feedback_receiver.ability_level = safe_increase(feedback_receiver.ability_level, 0.1)
                    feedback_receiver.satisfaction = safe_increase(feedback_receiver.satisfaction, 0.1)
                    feedback_giver.satisfaction = safe_decrease(feedback_giver.satisfaction, 0.01)

    

    def start_discussion(self, grant):
        """
        Starting a discussion means peeking at other reviewer's scores for a
        given grant. The reviewer that sparks the discussion updates their
        own score for the grant to be the mean of the other two.

        The reviewer that sparks the discussion increases their knowledge by 0.5
        points
        """

        # there are N reviewers per grant
        # let's randomly grab any one of them
        # and make them a potential discussion owner   
        r = range(3)     
        owner_idx = choice(r)
        owner = grant.reviewers[owner_idx]
        rand = randint(0,1) #dice roll
        if rand > owner.discussion_probability:

            #print("Having a discussion!")

            grant.discussed +=1
            
            partner_idxs = [x for x in r if x != owner_idx]
            
            partners = list(map(grant.reviewers.__getitem__, partner_idxs))
            partner_scores = list(map(grant.reviewer_scores.__getitem__, partner_idxs))
            partner_abilities = []
            for i in partner_idxs:
                partner_abilities.append([grant.reviewers[i].ability_level])

            # update owner's score for this grant
            # the owners score becomes the score of the partner with highest ability
            max_ability_idx = max(range(len(partner_abilities)), key=partner_abilities.__getitem__)
            grant.reviewer_scores[owner_idx] = partner_scores[max_ability_idx]
            owner.satisfaction = safe_increase(owner.satisfaction, 0.1) # please discussion owner
            owner.ability_level = safe_increase(owner.ability_level, 0.1)

            for partner in partners:
                # annoy partners
                partner.satisfaction = safe_decrease(partner.satisfaction, 0.01)


    def update_reviewer_metrics(config_file):
        """
        function updates the trust level and fee per review
        for all reviewers in pool when called
        """
        for reviewer in self.reviewers:
            reviewer.get_trust_level()
            reviewer.get_fee(config_file)


    def airdrop(self):
        """
        Gives top 3 reviewers (by ability) a poap
        """

        #print("POAP AIRDROP")
        sorted_reviewers = sorted(self.reviewers, key=operator.attrgetter("ability_level"))
        for reviewer in sorted_reviewers[0:3]:
            reviewer.poaps +=1
            reviewer.satisfaction = safe_increase(reviewer.satisfaction, 0.2)


class Grant():
    
    def __init__(self, value, clarity, legitimacy, grant_number):
        self.grant_number = grant_number
        self.value = value
        self.clarity = clarity
        self.legitimacy = legitimacy
        self.reviewer_scores = []
        self.reviewers = []
        self.aggregate = 0
        self.discussed =0
        self.unsafe = 0
        self.difficulty = self.calculate_difficulty()
        self.true_outcome = self.determine_true_grant_outcome()


    def calculate_difficulty(self):
        """
        calculates grant difficulty as the sum of
        pairwise differences between the grant attributes.
        This is because grants that score similarly across all
        metrics should be easy to score either positively or negatively.
        """

        # protect against negative values
        a = max(self.clarity, self.value) - min(self.clarity, self.value)
        b = max(self.clarity, self.legitimacy) - min(self.clarity, self.legitimacy)
        c = max(self.value, self.legitimacy) - min(self.value, self.legitimacy)

        difficulty = sum([a,b,c])

        # some values <0 and >1 are possible in edge cases of extreme differences
        # between attribute values. So we handle them.
        if difficulty<=0:
            difficulty = min(self.clarity, self.value, self.legitimacy)
        elif difficulty >= 1:
            difficulty = max(self.clarity, self.value, self.legitimacy)
        else:
            pass

        # validate value is bounded 0-1
        assert(0<difficulty and 1 > difficulty)

        return difficulty

    def determine_true_grant_outcome(self):
        """defines a "true" outcome for a grant - this is what
        how we want a reviewer to assess the grant.
        """

        if (sum([self.value, self.clarity])/2) > 0.5:
            return 1
        else:
            return 0


    def aggregate_score(self):
        """
        takes mean of reviewer scores
        and returns it as self.aggregate.
        """

        # mean + condition is effectively a 2/3 majority vote
        if sum(self.reviewer_scores)/len(self.reviewer_scores) < 0.5:
            self.aggregate = 0
        else:
            self.aggregate = 1
        
        return self.aggregate



class GrantPool():


    def __init__(self, grant_file):

        grant_dataframe = pd.read_csv(grant_file)
        grants = []

        for counter in range(len(grant_dataframe)):

            grant_number = grant_dataframe.iloc[counter].grant_number
            value = grant_dataframe.iloc[counter].value
            clarity = grant_dataframe.iloc[counter].clarity
            legitimacy = grant_dataframe.iloc[counter].legitimacy

            grant = Grant(value, clarity, legitimacy, grant_number)
            grants.append(grant)

        self.grants = grants



class FundingPool():
    def __init__(self, config_file):

        with open(config_file, "r") as ymlfile:
            inputs = yaml.load(ymlfile, Loader=yaml.FullLoader)
        
        self.balance = inputs["config"]["initial_pool_balance"]
        self.poap_balance = inputs["config"]["initial_poap_balance"]




class Report():

    def __init__(self, config_file):

        columns = []
        self.dataframe = pd.DataFrame()

        with open(config_file, "r") as ymlfile:
            inputs = yaml.load(ymlfile, Loader=yaml.FullLoader)

            try:
                for value in inputs["config"]["report_columns"]:
                    self.dataframe[str(value)] = 0
                    
            except:
                raise ValueError("problem parsing columns from yaml file to dataframe")
            
            self.savepath = inputs["config"]["savepath"]


    def update_report(self, grant):
        """
        collate all output data and write it to a csvfile
        columns are defined in config_file
        
        """

        # determine whether review was "correct" (i.e. did a reviewer
        # give it the score it was supposed to get?)
        # updates `reviewer_x_correct` in output df with bool
        # roll dice and use reviewer ability as likelihood of success

        n = random()
        correct = []
        for i in range(3):
            if grant.reviewers[i].ability_level>n:
                correct.append(1)
            else: 
                correct.append(0)

        row = [grant.round_number, 
                   int(grant.grant_number), 
                   grant.value, 
                   grant.clarity, 
                   grant.legitimacy,
                   grant.difficulty,
                   grant.unsafe,
                   grant.reviewers[0].reviewer_number,
                   grant.reviewers[0].social_level,
                   grant.reviewers[0].ability_level,
                   grant.reviewers[0].recognition_level,
                   grant.reviewers[0].engagement,
                   grant.reviewers[0].satisfaction,
                   grant.reviewers[0].balance,
                   grant.reviewers[0].trust_level,
                   correct[0],
                   grant.reviewers[1].reviewer_number,
                   grant.reviewers[1].social_level,
                   grant.reviewers[1].ability_level,
                   grant.reviewers[1].recognition_level,
                   grant.reviewers[1].engagement,
                   grant.reviewers[1].satisfaction,
                   grant.reviewers[1].balance,
                   grant.reviewers[1].trust_level,
                   correct[1],
                   grant.reviewers[2].reviewer_number,
                   grant.reviewers[2].social_level,
                   grant.reviewers[2].ability_level,
                   grant.reviewers[2].recognition_level,
                   grant.reviewers[2].engagement,
                   grant.reviewers[2].satisfaction,
                   grant.reviewers[2].balance,
                   grant.reviewers[2].trust_level,
                   correct[2],
                   grant.reviewer_scores[0],
                   grant.reviewer_scores[1],
                   grant.reviewer_scores[2],
                   grant.aggregate,
                   grant.discussed]
        
        self.dataframe.loc[len(self.dataframe)] = row

        return
    
    def save_to_file(self):

        self.dataframe.to_csv(str(self.savepath+"output-file.csv"))

        return

    
if __name__ == "__main__":
    pass