

def build_assert_text(ok_,eq_):
    def body(src, expect, save_words=None):
        src_it = iter(src.split())
        expect_it = iter(expect.split())
        look_until_match = False
        s1, s2 = None, None
        while True:
            try:
                s1 = next(src_it)
            except StopIteration:
                try:
                    s2 = next(expect_it)
                except StopIteration:
                    break
                print(src)
                ok_(False, 'expecting longer text %r %r' % (s1, s2))
            if look_until_match:
                if s2 == s1:
                    look_until_match = False
                continue
            try:
                s2 = next(expect_it)
            except StopIteration:
                print(src)
                ok_(False, 'expecting shorter text')
            if s2 == '....':
                look_until_match = True
                s2 = None
                try:
                    s2 = next(expect_it)
                except StopIteration:
                    pass
            elif s2 == '...':
                if save_words is not None:
                    save_words.append(s1)
            else:
                if s1 != s2:
                    print(src)
                    eq_(s1, s2)
    return body
