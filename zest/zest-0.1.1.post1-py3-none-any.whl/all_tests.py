test_list = []

def test_all(quiet_mode = False):
    lines = []
    count = len(test_list)
    lines.append("Test count: {}".format(count))
    failed = 0
    for test in test_list:
        test.do_test()
        if test.result:
            if quiet_mode:
                continue
        else:
            failed += 1
            lines.append("################IMPORTANT################")
        lines.append(str(test))
    lines.append("Passed: {0}/{1}, Failed {2}/{1}".format(count - failed, count, failed))
    if failed > 0:
        lines.append("Overall test failed.")
    else:
        lines.append("Overall test passed.")
    return "\n".join(lines)
        
        

        