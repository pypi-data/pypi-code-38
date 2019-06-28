import PythonMeta as MA

def showstudies(studies):    
    text = "%-10s %-20s %-20s \n"%("Study ID","Experiment Group","Control Group")
    text += "%-10s %-10s %-10s %-10s %-10s \n"%(" ","e1","n1","e2","n2")
    for i in range(len(studies)):
        text += "%-10s %-10s %-10s %-10s %-10s \n"%(studies[i][4],str(studies[i][0]),str(studies[i][1]),str(studies[i][2]),str(studies[i][3]))
    return text

def showresults(rults):
    text = "%-10s %-6s  %-18s %-10s"%("Study ID","n","ES(95% CI)","weight(%)\n")    
    for i in range(1,len(rults)):
        text += "%-10s %-6d  %-4.2f[%.2f %.2f]   %6.2f\n"%(
        rults[i][0],
        rults[i][5],
        rults[i][1],
        rults[i][3],
        rults[i][4],
        100*(rults[i][2]/rults[0][2])
        )
    text += "%-10s %-6d  %-4.2f[%.2f %.2f]   %6d\n"%(
        rults[0][0],
        rults[0][5],
        rults[0][1],
        rults[0][3],
        rults[0][4],
        100
        )  
    text += "%d studies included (N=%d)\n"%(len(rults)-1,rults[0][5])
    text += "Heterogeneity: Tau\u00b2=%.3f "%(rults[0][12]) if not rults[0][12]==None else "Heterogeneity: "
    text += "Q(Chisquare)=%.2f(p=%s); I\u00b2=%s\n"%(
        rults[0][7],
        rults[0][8],
        str(round(rults[0][9],2))+"%")
    text += "Overall effect test: z=%.2f, p=%s\n"%(rults[0][10],rults[0][11])
    
    return text

def main():
    d = MA.Data()
    f = MA.Fig()
    m = MA.Meta()
    
    d.datatype = 'CATE'
    studies = d.getdata(d.readfile('studies.txt'))
    print(showstudies(studies))

    m.datatype=d.datatype
    m.models = 'Fixed'
    m.algorithm = 'MH'    
    m.effect = 'RR'
    results = m.meta(studies)
    print(m.models + " " + m.algorithm + " " + m.effect)
    print (showresults(results))

    f.forest(results).show()
    
if __name__ == '__main__':
    main()

