# Rewards

This is a prototype agent-based model for simulating Gitcoin grant reviewer incentive models.

Start by defining a collection of reviewers in `reviewers.csv` and a set of grants in `grants.csv` or use the
defaults provided.

Then run `src/python main.py`

## Concept

- grants are defined in `grants.yaml` - they have `clarity`, `value` and `legitimacy` attributes.
- reviewers are defined in `reviewers.yaml` - they have `social_level`, `ability_level`, `recognition_level`, `engagement`, `discussion_probability` and `satisfaction` attributes.
- Individual grants are instances of the `Grant` class
- Individual reviewers are instances of the `Reviewer` class
- In each round, all the reviewers are collated into an instance of the `ReviewerPool` class.
- In each round, all the grants are collated into an instance of the `GrantsPool` class.
- The total amount of funding available is user-defined (in `model_config.yaml`) and provided as an attribute of the `Funding` class
- A grant is reviewed by a random trio of reviewers

A pipeline then takes instances of `ReviewerPool`, `GrantsPool` and `Funding` as arguments 

General rules:

- discussion owners are pleased to have discussions but their discussion partners are annoyed
- feedback pleases the recipient but annoys the givers
- feedback can only be from higher-trust-level to lower-trust-level
- receiving feedback or starting discussions increases ability
- reviewing grants increases ability
- reviewers are paid a fee to review. The fee is greater for higher trust reviewers.
- reviewers can also be rewarded with poaps
- as reviewer's ability increases so does their likelihood of correctly scoring a grant

The pipeline implements the following logic:

1) Iterate over grants in the grants pool. Pass each grant to each reviewer.
2) Each reviewer assesses the grant and receives a fee for doing so. The fee is determined by their trust-level
3) For each review there is a chance that someone in the review team will start a discussion with other reviewers. One of the three reviewers is randomly selected, and they might want to discuss. The probability of this is determined by the reviewers `discussion_probability` attribute. If a discussion is started the reviewer's score for a grant is the mean of two
discussion partners. The satisfaction score of the discussion owner increases, the satisfaction score of the partners decreases.
4) Some reviewers give feedback to others in each round. Feedback flows from higher to lower trust levels. Feedback increases the recipients
   ability level but slightly annoys the feedback giver.
5) After all reviewers have scored a grant, and any discussions have finished, an aggregate score for each grant is calculated.
6) The reviewer attributes are refreshed, taking into account learning within the round.


## How to use

1) clone this repo
2) navigate to top level project directory (`~/Rewards`)
3) run `python src/model/main.py`


## TODOs

1) update `make_decision()` function. At the moment it is a completely arbitrary placeholder. It should be some meaningful combination of grant and reviewer attributes.
2) The magnitude of payments, satisfaction increases and decreases, number of reviewers in discussions etc all need to be tuned. They are arbitrarily chosen at the moment
3) At the moment every reviewer sees every grant. We need to add some logic so that reviewers are divided across the grants.
   **Update** this is now replaced by logic that randomly assigns three reviewers per grant.
4) The model runs on dummy data, we need to determine how to wrangle real Gitcoin grants data intoa suitable format for running simulations
5) Determine sensible definition of trust level 1,2,3. In the prototype I take an arithmetic mean of [social_level, ability_level, recognition_level, engagement] each of which are normalized to 0-1. The mean is then used to determine trust-level as follows:
        
    L1 = mean <=0.5
    L2 = mean <=0.8
    L3 = mean > 0.8

6) At the moment all combinations of reviewers potentially give feedback to each other in every round. This probably isnt desirable behaviour. 