from .experience_parser import parse_experience


def test_parse():
    def str_list_match(str_list1, str_list2):
        if len(str_list1) != len(str_list2):
            return False
        for idx in range(len(str_list1)):
            if str_list1[idx] != str_list2[idx]:
                return False
        return True

    job_titles = ['accounting clerk', 'management assistant']

    exp1 = 'Two years of full-time paid experience as an Accounting Clerk'
    result1 = ['two', 'years', 'of', 'full-time', 'paid', 'experience',
               'as an', 'accounting clerk']
    assert str_list_match(result1, parse_experience(exp1.lower(), job_titles))

    exp2 = 'One year of full-time paid professional experience as a' \
        ' Management Assistant with the City of Los Angeles'
    result2 = ['one', 'year', 'of', 'full-time', 'paid', 'professional',
               'experience', 'as a', 'management assistant',
               'with the city of los angeles']
    assert str_list_match(result2, parse_experience(exp2.lower(), job_titles))

    exp3 = 'Three years of full-time paid experience' \
        ' with the City of Los Angeles as a Management Assistant'
    result3 = ['three', 'years', 'of', 'full-time', 'paid', 'experience',
               'with the city of los angeles', 'as a', 'management assistant']
    assert str_list_match(result3, parse_experience(exp3.lower(), job_titles))
