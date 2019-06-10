from __future__ import print_function
import webbrowser, time

class CV:
    blog_url: str = 'www.lishiyu.com'
    resume: str = '''
    ======================
    Mein Name ist lishiyu.
    I am lishiyu.
    我是李时雨。
    ======================
                  '''
    def __init__(self) -> None:
        pass

    def print_resume(self) -> None:
        print(self.resume)

    def goto_blog(self) -> None:
        webbrowser.open(self.blog_url)


def main() -> None:
    cv = CV()
    cv.print_resume()
    time.sleep(2)
    cv.goto_blog()

if __name__ == '__main__':
    main()
