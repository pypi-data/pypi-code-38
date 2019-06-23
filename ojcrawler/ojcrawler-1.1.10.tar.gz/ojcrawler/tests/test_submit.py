# -*- coding: utf-8 -*-
# Created by crazyX on 2018/7/7

from ojcrawler.control import Controller

import unittest
import os


class Test(unittest.TestCase):

    def setUp(self):
        self.ctl = Controller()
        self.ctl.load_accounts_json(os.path.join(os.getcwd(), 'accounts_sample.json'))

    def test_submit(self):
        pass
        # self.crawler_hdu()
        # self.crawler_poj()
        # self.crawler_cf()

    def test_crawler_hdu(self):
        pid = 1000
        lang = 'g++'
        ac_src = '''
        #include<bits/stdc++.h>
        using namespace std;
        int main()
        {
            int a,b;
            while(cin>>a>>b)cout<<a+b<<endl;
            return 0;
        }
        '''
        wa_src = '''
        #include<bits/stdc++.h>
        using namespace std;
        int main()
        {
            int a,b;
            while(cin>>a>>b)cout<<a-b<<endl;
            return 0;
        }
        '''
        self.ctl.add_task('hdu', ac_src, lang, pid)
        self.ctl.add_task('hdu', wa_src, lang, pid)
        import time
        time.sleep(5)

    def test_crawler_poj(self):
        pid = 1000
        lang = 'g++'
        wa_src = '''
        #include<iostream>
        using namespace std;
        int main()
        {
            int a,b;
            while(cin>>a>>b)cout<<a-b<<endl;
            return 0;
        }
        '''
        ac_src = '''
        #include<iostream>
        using namespace std;
        int main()
        {
            int a,b;
            while(cin>>a>>b)cout<<a+b<<endl;
            return 0;
        }
        '''
        self.ctl.add_task('poj', ac_src, lang, pid)
        self.ctl.add_task('poj', wa_src, lang, pid)
        import time
        time.sleep(20)

    def test_crawler_cf(self):
        pid = '1A'
        lang = 'GNU G++11 5.1.0'
        src = '''
        #include <iostream>
        using namespace std;
        int n,m,a;
        long long x,y;
        int main() {
            cin>>n>>m>>a;
            x=n/a+(n%a==0?0:1);
            y=m/a+(m%a==0?0:1);//sadjiowdqwdw
            cout<<x*y<<endl;
            return 0;
            //fuck you you
        }
        '''
        self.ctl.add_task('codeforces', src, lang, pid)
        import time
        time.sleep(20)


if __name__ == '__main__':
    unittest.main()
