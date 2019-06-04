from bpg.bpg import Version
def testVersionCreatedFromString() :
    s = '1.0.2'
    version = Version(s)
    
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 2
    
def testVersionCompare() :
    v1 = Version('1.0.2')
    v2 = Version('2.0.0')
    v3 = Version('3.1.0')
    assert v1 < v2
    assert v3 > v2
    
def testSortVersion() :
    v1 = Version('1.0.2')
    v2 = Version('2.0.0')
    v3 = Version('3.1.0')
    versions = [v1,v2,v3]
    versions.sort(reverse=True)
    assert v1 == versions[2]
    
def testVersionPatchOptional():
    v1 = Version('1.0.2')
    assert v1.major == 1
    assert v1.minor == 0
    assert v1.patch == 2
    
    v2 = Version('1.0')
    assert v2.major == 1
    assert v2.minor == 0
    assert not v2.patch 

    


    
    

    