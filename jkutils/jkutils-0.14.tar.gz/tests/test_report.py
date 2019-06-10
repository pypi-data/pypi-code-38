from jkutils.report_exception import AbnormalReport


def test_report():
    ar = AbnormalReport("jkutils", "test", "http://httpbin.org/post")
    ar.set_err_code(1, 2, 3)
    ar.report("这是一个测试", "出 bug 啦～～～")
