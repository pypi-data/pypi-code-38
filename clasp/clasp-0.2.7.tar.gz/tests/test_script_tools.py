"""py.test for script_tools.py"""
import clasp.script_tools as mgr
import os
#pytest -s -v test_script_tools.py

def test_pipeline():
    """py.test for pipeline"""
    data = [
    (["pcomb -x 100 -y 100 -e 'lo=1'","pvalue -o -b -h -d -H","total"],),
    (["pcomb -x 100 -y 100 -e 'lo=1'","pfilt -1 -e 1 -x 200 -y 200"],open("test.hdr",'w'),None,True),
    (["rcalc -e '$1=$1*$2;$2=$2;$3=$1'"],None,"2 3"),
    (["rcalc -e '$1=$1*$2;$2=$2;$3=$1'","total"],None,"2 3")]
    answer = ['9961\n',None,'6\t3\t2\n','6\t3\t2\n']
    for d,a in zip(data,answer):
        result = mgr.pipeline(*d)
        assert result == a
    os.system("rm test.hdr")

def test_cluster_call():
    """py.test for cluster_call"""
    
    def fac(b):
        def test(a,b):
            """return a*b!"""
            if b == 1:
                return a
            else:
                return test(a*b,b-1)
        return test(1,b)
    data = [
    (fac,(range(1,10),))
    ]
    answer = [[1,2,6,24,120,720,5040,40320,362880]]
    for d,a in zip(data,answer):
        result = mgr.cluster_call(*d)
        assert result == a


def test_kwarg_match():
    """py.test for kwarg_match"""
    
    def crop_reg(imagein, imageout, width=None, height=None, left=0,
                 bottom=0, scale=1.0, colorcor="", **kwargs):
        pass
    data = {
        'width':None, 'height':None, 'left':0,
                         'bottom':0, 'scale':1.0, 'colorcor':"", 'empty':9999
    }
    answer = {
        'width':None, 'height':None, 'left':0,
                         'bottom':0, 'scale':1.0, 'colorcor':""
    }
    assert mgr.kwarg_match(crop_reg, data) == answer


def test_kwarg_arg():
    """py.test for kwarg_match"""
    
    def crop_reg(imagein, imageout, width=None, height=None, left=0,
                 bottom=0, scale=1.0, colorcor="", **kwargs):
        pass
    data = {
        'left':0, 'bottom':0, 'scale':3.0, 'colorcor':"", 'empty':9999
    }
    answer = [None, None, 0, 0, 3.0, ""]
    assert mgr.kwarg_arg(crop_reg, data) == answer