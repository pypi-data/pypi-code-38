def quiz_result(voter, questions=None):
    if questions is None:
        questions = voter.voted_questions

    if not questions:
        return None

    numerator = 0
    denominator = 0
    answers_count = 0

    for question in questions:
        if not question.is_quiz:
            continue

        result = voter.get_question_result(question)

        if result is None:
            continue

        correct_options = question.option_set.filter(is_correct=True).count()

        if correct_options == 0:
            correct_options = question.option_set.count()

        answers = voter.answer_set.filter(question=question)
        answers_count += answers.count()

        numerator += correct_options * result
        denominator += correct_options

    # 0 correct options, but marked some => WRONG
    if denominator == 0 and answers_count != 0:
        return 0

    # 0 correct options and not marked any => CORRECT
    if denominator == 0 and answers_count == 0:
        return 100

    total_result = float(numerator) * 100 / denominator
    return round(total_result, 2)
