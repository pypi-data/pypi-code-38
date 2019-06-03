from votebase.core.voting.models import Voter


def limit_answers(answers, survey):
    voters_limit = survey.user.get_profile().get_voters_limit()

    if answers.count() <= voters_limit:
        return answers

    first_voters_ids = Voter.objects.values_list('id', flat=True)\
                       .filter(survey=survey)\
                       .order_by('id')[:voters_limit]
    max_voter_id = first_voters_ids[len(first_voters_ids)-1]
    return answers.filter(voter__id__lte=max_voter_id)


def limit_voters(voters, survey):
    voters_limit = survey.user.get_profile().get_voters_limit()

    if voters.count() <= voters_limit:
        return voters

    first_voters_ids = Voter.objects.values_list('id', flat=True)\
                       .filter(survey=survey)\
                       .order_by('id')[:voters_limit]
    max_voter_id = first_voters_ids[len(first_voters_ids)-1]
    return voters.filter(id__lte=max_voter_id)
