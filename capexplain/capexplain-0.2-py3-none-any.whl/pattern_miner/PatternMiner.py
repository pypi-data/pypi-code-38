import sys
import pprint
import logging
import pandas as pd
from itertools import combinations
from time import sleep,time
import statsmodels.formula.api as sm
from psycopg2.extras import Json
from sklearn.linear_model import LinearRegression
from scipy.stats import chisquare, mode
from numpy import percentile, mean
from capexplain.pattern_miner.permtest import findpre
from inspect import currentframe, getframeinfo
from capexplain.utils import printException, CombinationsWithLen, progress_iter, PermutationsWithLen
from capexplain.fd.fd import closure
from capexplain.cl.cfgoption import DictLike
from capexplain.cl.instrumentation import ExecStats


# setup logging
log = logging.getLogger(__name__)

# ********************************************************************************
class MinerConfig(DictLike):
    """
    MinerConfig - configuration for the pattern mining algorithm
    """

    ALGORITHMS={'naive','naive_alternative','optimized'}
    STATS_MODELS={'statsmodels','sklearn'}
    
    def __init__(self,
                 conn=None,
                 table=None,
                 pattern_schema='pattern',
                 fit=True,
                 theta_c=0.1,
                 theta_l=0.1,
                 lamb=0.1,
                 dist_thre=0.99,
                 reg_package='statsmodels',
                 supp_l=10,
                 supp_g=100,
                 fd_check=True,
                 supp_inf=True,
                 manual_num=False,
                 algorithm='optimized',
                 showProgress=True):
        self.conn=conn
        self.theta_c=theta_c
        self.theta_l=theta_l
        self.lamb=lamb
        self.fit=fit
        self.dist_thre=dist_thre
        self.reg_package=reg_package
        self.supp_l=supp_l
        self.supp_g=supp_g
        self.fd_check=fd_check
        self.supp_inf=supp_inf
        self.manual_num=manual_num
        self.algorithm=algorithm
        self.table=table
        self.pattern_schema=pattern_schema
        self.showProgress=showProgress
        log.debug("created miner configuration:\n%s", self.__dict__)
    
    def validateConfiguration(self):
        """
        Validate configuration.
        """
        log.debug("validate miner configuration ...")
        if self.reg_package not in self.STATS_MODELS:
            log.warning('Invalid input for reg_package, reset to default')
            self.reg_package='statsmodels'
        if self.algorithm not in self.ALGORITHMS:
            log.warning('Invalid input for algorithm, reset to default')
            self.algorithm='optimized'
        if self.table is None:
            log.error("user did not specify table for mining")
            raise Exception('please specify a table to mine')
        log.debug("validation of miner configuration successful:\n%s", self.__dict__)
        return True

    def __str__(self):
        return self.__dict__.__str__()
    
    def printConfig(self):
        pprint.pprint(self.__dict__)


# ********************************************************************************
class MinerStats(ExecStats):
    """
    Statistics gathered during mining
    """

    TIMERS={'aggregate',
            'df',
            'regression',
            'insertion',
            'drop',
            'loop',
            'innerloop',
            'fd_detect',
            'check_fd',
            'total',
            'query_cube',
            'query_materializecube',
    }

    COUNTERS={'patcand.local',
              'patcand.global',
              'patterns.local',
              'patterns.global',
              'query.agg',
              'query.sort',
              'G',
              'F,V'
    }


# ********************************************************************************
class PatternFinder:
    """
    Mining patterns for an input relation. Patterns are stored in a table X
    """

    config=None
    stats=None

    glob=None #global patterns
    num_rows=None #number of rows of config.table
    num=None #numeric attributes
    summable=None#summable attributes
    n=None#number of attributes
    grouping_attr=None #attributes can be in group
    schema=None #list of all attributes
    time=None #record running time for each section
    superkey=None #used to track compound key
    failedf=None #used to apply support inference
    group_rows=None #track # of rows for each group, used for fd check
    
    def __init__(self, config : MinerConfig):
        self.config = config
        self.initDataStructures()
        log.debug("initialized datastructures")
        self.fetchInputTableInfo()
        log.info("fetched basic table information - ready to mine")

    def fetchInputTableInfo(self):
        try:
            self.schema=list(pd.read_sql("SELECT * FROM "+self.config.table+" LIMIT 1",self.config.conn))
        except Exception as ex:
            printException(ex, getframeinfo(currentframe()))
            sys.exit(2)
        self.n=len(self.schema)
        log.debug("fetched schema for input table: %s with %d attributes", self.schema, self.n)        
            
        self.num_rows=pd.read_sql("SELECT count(*) as num from "+self.config.table,self.config.conn)['num'][0]
        log.debug("input table has %d rows", self.num_rows)

        #check uniqueness, grouping_attr contains only non-unique attributes
        unique=pd.read_sql("SELECT "+','.join(["count(distinct "+attr+") as "+attr for attr in self.schema])+ " FROM "+self.config.table,
                                              self.config.conn)                            
        for attr in self.schema:
            #aggresive approach:
            n_distinct=unique[attr][0]
            if n_distinct>=self.num_rows*self.config.dist_thre:
                continue
            self.grouping_attr.append(attr)
            self.group_rows[frozenset([attr])]=n_distinct

        log.debug("possible grouping attributes: %s", self.grouping_attr)
                
        for col in self.schema:
            try: # Boris: this may fail, better to get the datatype from the catalog and have a list of numeric datatypes to check for
                self.config.conn.execute("SELECT CAST("+col+" AS NUMERIC) FROM "+self.config.table)
                self.num.append(col)
            except:
                continue
        if self.config.manual_num:
            self.setNumeric()
        else:
            self.summable=self.num
        log.debug("tables has numerical attributes %s and summable attributes", self.num, self.summable)

    def progress(self, iter, desc=None):
        return progress_iter(iter=iter, desc=desc, showProgress=self.config.showProgress)
        
    def initDataStructures(self):
        self.stats = MinerStats()
        self.superkey=set()        
        self.num=[]
        self.grouping_attr=[]
        self.group_rows={}
        
    def setNumeric(self):
        print("Current Numeric: ")
        print(self.num)
        if input('Redefine? (y/n, default n)')=='y':
            num=[]
            for attr in self.num:
                keep=input('Keep '+attr+' as Numeric?(y/n,default y)')
                if keep=='n':
                    continue
                else:
                    num.append(attr)
            self.num=num
            self.summable=[attr for attr in self.summable if attr in num]
        print("Current Summable: ")
        print(self.summable)
        if input('Redefine? (y/n, default n)')=='y':
            summable=[]
            for attr in self.summable:
                keep=input('Keep '+attr+' as Summable?(y/n,default y)')
                if keep=='n':
                    continue
                else:
                    summable.append(attr)
            self.summable=summable
        
    def validateFd(self,group,division=None):
        '''
        check if we want to ignore f=group[:division], v=group[division:]
        type group: tuple of strings
        
        return True if group is valid
        return False if we decide to ignore it
        
        if division=None, check all possible divisions, and return boolean[]
        '''
        if division:
            if not self.config.fd_check:
                return True
            if division==1:
                return True
            row=self.group_rows[frozenset(group[:division])]
            for i in group[:division]:
                if self.group_rows[frozenset([k for k in group[:division] if k!=i])]>=row*self.config.dist_thre:
                    return False
            return True
        else:
            n=len(group)
            ret=[self.validateFd(group,i) for i in range(1,n)] #division from 1 to n-1
            return ret
            
    def findPattern(self,user=None):
        if (self.config.showProgress):
            print(" MINING PATTERNS FOR: {}".format(self.config.table))
#       self.pc=PC.PatternCollection(list(self.schema))
        self.glob=[]#reset self.glob
        self.createTable(self.config.pattern_schema)
        self.stats.startTimer('total')
        if not user:
            grouping_attr=self.grouping_attr
            aList=self.summable+['*']
        else:
            log.debug("user provided list of group-by and aggregation input attributes %s", user)
            grouping_attr=user['group']
            aList=user['a']
        log.debug("mine patterns for group-by attrs %s and aggregate input attributes %s", grouping_attr, aList)
        
        if self.config.algorithm=='naive':# CUBE ALGORITHM
            for a in self.progress(aList, desc='agg functions'):
                if not user:
                    if a=='*':#For count, only do a count(*)
                        agg="count"
                    else: #a in self.num
                        agg="sum"
                else:
                    agg=user['agg']
    
                log.debug("consider aggregation %s(%s) ", agg, a)
                #for agg in aggList :
                cols=[col for col in grouping_attr if col!=a]
                n=len(cols)
                self.formCube(a, agg, cols)
                for size in self.progress(range(min(4,n),1,-1), desc='pattern size'):
                    combs=CombinationsWithLen(cols,size)
                    for group in self.progress(combs, desc='F,V combinations'):#comb=f+v
                        self.stats.incr('G')
                        log.debug("consider group-by attributes %s", group)
                        for fsize in self.progress(range(1,len(group)), desc='F size'):
                            fs=CombinationsWithLen(group,fsize)
                            for f in self.progress(fs, desc='F'):
                                self.stats.incr('F,V')
                                self.stats.incr('patcand.global')
                                log.debug("consider group-by attributes %s with F=%s", group, f)
                                self.fit_naive(f,group,a,agg,cols)
                self.dropCube()
        else:#self.config.algorithm=='optimized' or self.config.algorithm=='naive_alternative'
            self.failedf=set()
            for size in self.progress(range(2,min(4,len(grouping_attr))+1),desc='pattern size'):
                for group in self.progress(combinations(grouping_attr,size), desc='group'):
                    for i in self.superkey:
                        if set(i).issubset(group):
                            break
                    else:#doesn't contain superkey
                        aggList=[]
                        for a in aList:
                            if a in group:
                                continue
                            if a=='*':
                                aggList.append('count')
                            else:
                                aggList.append('sum_'+a+'')
                        if len(aggList)==0:
                            continue
                        self.aggQuery(group, aList)
                        self.stats.startTimer('fd_detect')
                        isSuperkey=False
                        if self.config.fd_check:
                            cur_rows=pd.read_sql('SELECT count(*) as num FROM agg',con=self.config.conn)['num'][0]
                            if cur_rows>=self.num_rows*self.config.dist_thre:
                                self.superkey.add(group)
                                isSuperkey=True
                            self.group_rows[frozenset(group)]=cur_rows
                        self.stats.stopTimer('fd_detect')
                        if not isSuperkey:
                            if self.config.algorithm=='naive_alternative':
                                for fsize in self.progress(range(size-1,0,-1),desc='Fsize'):
                                    for f in self.progress(combinations(group,fsize),desc='F'):
                                        self.stats.startTimer('df')
                                        df=pd.read_sql('SELECT * FROM agg ORDER BY '+','.join(f),con=self.config.conn)
                                        self.stats.stopTimer('df')
                                        grouping=tuple([fattr for fattr in f]+[vattr for vattr in group if vattr not in f])
                                        division=len(f)
                                        self.fitmodel(df, grouping, aggList, division)  
                            else:#algorithm='optimized'
                                for i in self.progress(range(len(group)),desc='Group size'):
                                    perm=group[i:]+group[:i]
                                    self.stats.startTimer('df')
                                    df=pd.read_sql('SELECT * FROM agg ORDER BY '+','.join(perm[:-1]),con=self.config.conn)
                                    self.stats.stopTimer('df')
                                    self.fitmodel(df, perm, aggList, None)
                                if len(group)==4:
                                    for f in [(group[0],group[2]),(group[1],group[3])]:
                                        grouping=tuple([fattr for fattr in f]+[vattr for vattr in group if vattr not in f])
                                        division=len(f)
                                        self.stats.startTimer('check_fd')
                                        fd_val=self.validateFd(grouping, division)
                                        self.stats.stopTimer('check_fd')
                                        if fd_val:
                                            self.stats.startTimer('df')
                                            df=pd.read_sql('SELECT * FROM agg ORDER BY '+','.join(f),con=self.config.conn)
                                            self.stats.stopTimer('df')
                                            self.fitmodel(df, grouping, aggList, division)       
                        self.dropAgg()    
        if self.glob:
            self.stats.startTimer('insertion')
            self.config.conn.execute("INSERT INTO "+self.config.pattern_schema+"."+self.config.table+"_global values"+','.join(self.glob))
            self.stats.stopTimer('insertion')
        self.stats.stopTimer('total')
        self.insertTime('\''+self.config.table+'_num_global:'+str(len(self.glob))+' algo:'+self.config.algorithm+'\'')
        log.warning("pattern mining finished: time stats:\n\n%s", self.stats.formatStats())
        if (self.config.showProgress):
            sleep(0.5)
            print("\n\n\n\n\nFINISHED MINING PATTERNS FOR {} found {} global patterns based on {} local patterns\n\n"
                  .format(self.config.table, self.stats.getCounter('patterns.global'), self.stats.getCounter('patterns.local')))
        
    def formCube(self, a, agg, attr):
        self.stats.startTimer('query_materializecube')
        self.stats.incr('query.agg')
        group=",".join(["CAST("+num+" AS NUMERIC)" for num in attr if num in self.num]+
                        [cat for cat in attr if cat not in self.num])
        grouping=",".join(["CAST("+num+" AS NUMERIC), GROUPING(CAST("+num+" AS NUMERIC)) as g_"+num
                        for num in attr if num in self.num]+
            [cat+", GROUPING("+cat+") as g_"+cat for cat in attr if cat not in self.num])
        if a in self.num:
            qa="CAST("+a+" AS NUMERIC)"
        else:
            qa=a
        if agg=='count':
            name='count'
        else:
            name='sum_'+a
        self.config.conn.execute("DROP TABLE IF EXISTS cube")
        query="CREATE TABLE cube AS SELECT "+agg+"("+qa+") AS \""+name+"\", "+group+','+grouping+" FROM "+self.config.table+"\
        "+"GROUP BY CUBE("+group+") having "+'+'.join(['grouping('+att+')' if att not in self.num 
                                else "GROUPING(CAST("+att+" AS NUMERIC))" for att in attr])+'>='+str(len(attr)-4)
        log.debug("Materialize CUBE:\n\n%s", query)
        self.config.conn.execute(query)        
        self.stats.stopTimer('query_materializecube')

    def dropCube(self):
        log.debug("DROP materialized CUBE")
        self.config.conn.execute("DROP TABLE cube;")
        
    def cubeQuery(self, g, f, cols):
        self.stats.startTimer('query_cube')
        self.stats.incr('query.sort')
        res=" and ".join(["g_"+a+"=0" for a in g])
        if len(g)<len(cols):
            unused=" and ".join(["g_"+b+"=1" for b in cols if b not in g])
            res=res+" and "+unused
        query= "SELECT * FROM cube where "+res+" ORDER BY "+",".join(f)
        log.debug("Run query over materialized CUBE:\n\n %s", query)
        self.stats.stopTimer('query_cube')
        return query
    
    def fit_naive(self,f,group,a,agg,cols):
        self.failedf=set()#to not trigger error
        fd=pd.read_sql(self.cubeQuery(group, f, cols),self.config.conn)
        g=tuple([att for att in f]+[attr for attr in group if attr not in f])
        division=len(f)
        if a=='*':
            aggList=['count']
        else:
            aggList=[agg+'_'+a]
        self.fitmodel_with_division(fd, g, aggList, division)
        
    def findPattern_inline(self,group,a,agg):
        #loop through permutations of group
        user={'group':group,'a':[a],'agg':agg}
        self.findPattern(user)
        
    def aggQuery(self, g, aList):
        self.stats.startTimer('aggregate')
        group=",".join(["CAST("+att+" AS NUMERIC)" if att in self.num else att for att in g])
        agg=[]
        for a in aList:
            if a in g:
                continue
            if a=='*':
                agg.append('count(*) AS \"count\"')
            else:
                agg.append('sum(CAST('+a+' AS NUMERIC)) AS \"sum_'+a+'\"')
        query="CREATE TEMP TABLE agg as SELECT "+group+","+','.join(agg)+" FROM "+self.config.table+" GROUP BY "+group
        self.config.conn.execute(query)
        self.stats.stopTimer('aggregate')
    
    def rollupQuery(self, group, d_index, agg):
        self.stats.startTimer('aggregate')
        grouping=",".join([attr+", GROUPING("+attr+") as g_"+attr for attr in group[:d_index]])
#        gsets=','.join(['('+','.join(group[:prefix])+')' for prefix in range(d_index,pre,-1)])
        self.config.conn.execute('CREATE TEMP TABLE grouping AS '+
                        'SELECT '+grouping+', SUM('+agg+') as '+agg+
#                        ' FROM agg GROUP BY GROUPING SETS('+gsets+')'+
                        ' FROM agg GROUP BY ROLLUP('+','.join(group)+')'+
                        ' ORDER BY '+','.join(group[:d_index]))
        self.stats.stopTimer('aggregate')
        
    def dropRollup(self):
        self.stats.startTimer('drop')
        self.config.conn.execute('DROP TABLE grouping')
        self.stats.stopTimer('drop')
        
    def dropAgg(self):
        self.stats.startTimer('drop')
        self.config.conn.execute('DROP TABLE agg')
        self.stats.stopTimer('drop')
        
    def fitmodel(self, fd, group, aggList, division):
        self.stats.startTimer('loop')
        if division:
            self.fitmodel_with_division(fd, group, aggList, division)
        else:
            self.fitmodel_no_division(fd, group, aggList)
        self.stats.stopTimer('loop')
            
    def fitmodel_no_division(self, fd, group, aggList):
        size=len(group)-1
        oldKey=None
        oldIndex=[0]*size
        num_f=[0]*size
        valid_l_f=[0]*size
        valid_c_f=[0]*size
        f=[list(group[:i]) for i in range(1,size+1)]
        v=[list(group[j:]) for j in range(1,size+1)]
        supp_valid=[group[:i] not in self.failedf for i in range(1,size+1)]
        f_dict=[{} for i in range(1,size+1)]
        self.stats.startTimer('check_fd')
        fd_valid=self.validateFd(group)
        self.stats.startTimer('check_fd')
        sample_invalid=[{} for i in range(size)]
        global_dev_pos=[{} for i in range(size)]
        global_dev_neg=[{} for i in range(size)]
        for i in range(size):
            for agg in aggList:
                global_dev_pos[i][agg]={}
                global_dev_pos[i][agg]['l']=float('-inf')
                global_dev_pos[i][agg]['c']=float('-inf')
                global_dev_neg[i][agg]={}
                global_dev_neg[i][agg]['l']=float('inf')
                global_dev_neg[i][agg]['c']=float('inf')
        if not any(fd_valid) or not any(supp_valid):
            return
        pattern=[]
        def fit(df,fval,i,n):
            if not self.config.fit:
                return
            self.stats.startTimer('regression')
            for agg in aggList:
                nonlocal global_dev_pos,global_dev_neg
                if agg not in sample_invalid[i] or 'c' not in sample_invalid[i][agg]:
                    avg=mean(df[agg])
                    describe=[avg,mode(df[agg]),percentile(df[agg],25)
                              ,percentile(df[agg],50),percentile(df[agg],75)]
                    dev_pos=max(df[agg])-avg
                    dev_neg=min(df[agg])-avg
                    #fitting constant
                    theta_c=chisquare(df[agg].dropna())[1]
                    if theta_c>self.config.theta_c:
                        nonlocal valid_c_f
                        try:
                            valid_c_f[i][agg]+=1
                        except KeyError:
                            valid_c_f[i][agg]=1
                        global_dev_pos[i][agg]['c']=max(global_dev_pos[i][agg]['c'],dev_pos)
                        global_dev_neg[i][agg]['c']=min(global_dev_neg[i][agg]['c'],dev_neg)
                        #self.pc.add_local(f,oldKey,v,a,agg,'const',theta_c)
                        pattern.append(self.addLocal(f[i],fval,v[i],agg,'const',theta_c,describe,'NULL',
                                                     dev_pos,dev_neg))
                        self.stats.incr('patterns.local')
              
                #fitting linear
                if agg not in sample_invalid[i] or 'l' not in sample_invalid[i][agg]:
                    if  theta_c!=1 and ((self.config.reg_package=='sklearn' and all(attr in self.num for attr in v[i])
                                        or
                                        (self.config.reg_package=='statsmodels' and all(attr in self.num for attr in v[i])))):
        
                        if self.config.reg_package=='sklearn':   
                            lr=LinearRegression()
                            lr.fit(df[v[i]],df[agg])
                            theta_l=lr.score(df[v[i]],df[agg])
                            theta_l=1-(1-theta_l)*(n-1)/(n-len(v[i])-1)
                            param=lr.coef_.tolist()
                            param.append(lr.intercept_.tolist())
                            param="'"+str(param)+"'"
                        else: #statsmodels
                            if n<=len(v[i])+1:#negative R^2 for sure
                                return
                            lr=sm.ols(agg+'~'+'+'.join([attr if attr in self.num else 'C('+attr+')' for attr in v[i]])
                                      ,data=df,missing='drop').fit()
                            theta_l=lr.rsquared_adj
                            param=Json(dict(lr.params))
                            dev_pos=max(lr.resid)
                            dev_neg=min(lr.resid)
                        
                        if theta_l and theta_l>self.config.theta_l:
                            nonlocal valid_l_f
                            try:
                                valid_l_f[i][agg]+=1
                            except KeyError:
                                valid_l_f[i][agg]=1
                            global_dev_pos[i][agg]['l']=max(global_dev_pos[i][agg]['l'],dev_pos)
                            global_dev_neg[i][agg]['l']=min(global_dev_neg[i][agg]['l'],dev_neg)
                            pattern.append(self.addLocal(f[i],fval,v[i],agg,'linear',theta_l,describe,param,
                                                         dev_pos,dev_neg))
                            self.stats.incr('patterns.local')
                        
            self.stats.stopTimer('regression')
            
        self.stats.startTimer('innerloop')
 
        for tup in fd.itertuples():
            
            position=None
            if oldKey:
                for i in range(size):
                    if getattr(tup,group[i])!=getattr(oldKey,group[i]):
                        position=i
                        break 
            
            if position is not None:
                index=tup.Index
                for i in range(position,size):
                    if not fd_valid[i] or not supp_valid[i]:
                        continue
                    n=index-oldIndex[i]
                    if n>=self.config.supp_l:
                        num_f[i]+=1
                        fval=tuple([getattr(oldKey,j) for j in f[i]])
                        f_dict[i][fval]=[oldIndex[i],index]
                    oldIndex[i]=index
                    
            oldKey=tup
            
        if oldKey:
            for i in range(size):
                if not fd_valid[i] or not supp_valid[i]:
                    continue
                n=oldKey.Index-oldIndex[i]+1
                if n>self.config.supp_l:
                    num_f[i]+=1
                    fval=tuple([getattr(oldKey,j) for j in f[i]])
                    f_dict[i][fval]=[oldIndex[i]]
        self.stats.stopTimer('innerloop')
        
        for i in range(size):
            if len(f_dict[i])<self.config.supp_g:
                if self.config.supp_inf:#if toggle is on
                    self.failedf.add(tuple(f[i]))
                supp_valid[i]=False
            else:
                for fval in f_dict[i]:
                    indices=f_dict[i][fval]
                    if len(indices)==2: #indices=[oldIndex,index]
                        fit(fd[indices[0]:indices[1]],fval,i,indices[1]-indices[0])
                    else: #indices=[oldIndex]
                        fit(fd[indices[0]:],fval,i,oldKey.Index-indices[0]+1)
                    
        #sifting global            
        for i in range(size):
            if not fd_valid[i] or not supp_valid[i]:
                    continue
            for agg in valid_c_f[i]:
                if agg in sample_invalid[i] and 'c' in sample_invalid[i][agg]:
                    continue
                lamb_c=valid_c_f[i][agg]/num_f[i]
                if valid_c_f[i][agg]>=self.config.supp_g and lamb_c>self.config.lamb:
                    self.glob.append(self.addGlobal(f[i],v[i],agg,'const',self.config.theta_c,lamb_c,
                                                    global_dev_pos[i][agg]['c'],global_dev_neg[i][agg]['c']))
            
            for agg in valid_l_f[i]:
                if agg in sample_invalid[i] and 'l' in sample_invalid[i][agg]:
                    continue
                lamb_l=valid_l_f[i][agg]/num_f[i]
                if valid_l_f[i][agg]>=self.config.supp_g and lamb_l>self.config.lamb:
                    self.glob.append(self.addGlobal(f[i],v[i],agg,'linear',self.config.theta_l,lamb_l,
                                                    global_dev_pos[i][agg]['l'],global_dev_neg[i][agg]['l']))
        
        if not self.config.fit:
            return 

        if pattern:
            self.stats.startTimer('insertion')
            self.config.conn.execute("INSERT INTO "+self.config.pattern_schema+"."+self.config.table+"_local values"+','.join(pattern))        
            self.stats.stopTimer('insertion')

    def fitmodel_with_division(self, fd, group, aggList, division):  
        if group[:division] in self.failedf:
            log.debug("do not consider already failed F=%s", group[:division])
            return
        
        oldKey=None
        oldIndex=0
        num_f=0
        valid_l_f={}
        valid_c_f={}
        f=list(group[:division])
        v=list(group[division:])
        log.debug("fitting patterns for F=%s, V=%s", f, v)
        sample_invalid={}
        global_dev_pos={}
        global_dev_neg={}
        for agg in aggList:
            global_dev_pos[agg]={}
            global_dev_pos[agg]['l']=float('-inf')
            global_dev_pos[agg]['c']=float('-inf')
            global_dev_neg[agg]={}
            global_dev_neg[agg]['l']=float('inf')
            global_dev_neg[agg]['c']=float('inf')
        #df:dataframe n:length    
        pattern=[]
        def fit(df,f,fval,v,n):
            self.stats.incr('patcand.local')
            if not self.config.fit:
                return
            log.debug("do regression for F=%s, f=%s", f, fval)
            self.stats.startTimer('regression')
            for agg in aggList:
                nonlocal global_dev_pos,global_dev_neg
                if agg not in sample_invalid or 'c' not in sample_invalid[agg]:
                    avg=mean(df[agg])
                    describe=[avg,mode(df[agg]),percentile(df[agg],25)
                                                  ,percentile(df[agg],50),percentile(df[agg],75)]
                    dev_pos=max(df[agg])-avg
                    dev_neg=min(df[agg])-avg                    
                    #fitting constant
                    theta_c=chisquare(df[agg].dropna())[1]
                    if theta_c>self.config.theta_c:
                        nonlocal valid_c_f
                        try:
                            valid_c_f[agg]+=1
                        except KeyError:
                            valid_c_f[agg]=1
                        global_dev_pos[agg]['c']=max(global_dev_pos[agg]['c'],dev_pos)
                        global_dev_neg[agg]['c']=min(global_dev_neg[agg]['c'],dev_neg)

                        pattern.append(self.addLocal(f,fval,v,agg,'const',theta_c,describe,'NULL',
                                                     dev_pos,dev_neg))
                        self.stats.incr('patterns.local')
                
                #fitting linear
                if agg not in sample_invalid or 'l' not in sample_invalid[agg]:
                    if  theta_c!=1 and ((self.config.reg_package=='sklearn' and all(attr in self.num for attr in v)
                                        or
                                        (self.config.reg_package=='statsmodels' and all(attr in self.num for attr in v)))):
        
                        if self.config.reg_package=='sklearn': 
                            lr=LinearRegression()
                            lr.fit(df[v],df[agg])
                            theta_l=lr.score(df[v],df[agg])
                            theta_l=1-(1-theta_l)*(n-1)/(n-len(v)-1)
                            param=lr.coef_.tolist()
                            param.append(lr.intercept_.tolist())
                            param="'"+str(param)+"'"
                        else: #statsmodels
                            if n<=len(v)+1:#negative R^2 for sure
                                return
                            lr=sm.ols(agg+'~'+'+'.join([attr if attr in self.num else 'C('+attr+')' for attr in v]),
                                      data=df,missing='drop').fit()
                            #theta_l=lr.rsquared_adj
                            theta_l=chisquare(df[agg],lr.predict())[1]
                            param=Json(dict(lr.params))
                            dev_pos=max(lr.resid)
                            dev_neg=min(lr.resid)
                            
                        if theta_l and theta_l>self.config.theta_l:
                            nonlocal valid_l_f
                            try:
                                valid_l_f[agg]+=1
                            except KeyError:
                                valid_l_f[agg]=1
                            global_dev_pos[agg]['l']=max(global_dev_pos[agg]['l'],dev_pos)
                            global_dev_neg[agg]['l']=min(global_dev_neg[agg]['l'],dev_neg)
                            pattern.append(self.addLocal(f,fval,v,agg,'linear',theta_l,describe,param,
                                                         dev_pos,dev_neg))
                            self.stats.incr('patterns.local')
                    
            self.stats.stopTimer('regression')
        
        self.stats.startTimer('innerloop')
        change=False
        f_dict={}
        for tup in fd.itertuples():
            if oldKey:
                change=any([getattr(tup,attr)!=getattr(oldKey,attr) for attr in f])
            if change:
                index=tup.Index
                n=index-oldIndex
                if n>=self.config.supp_l:
                    num_f+=1
                    fval=tuple([getattr(oldKey,j) for j in f])
                    log.debug("local support high enough for %s (%d > %d)", fval, n, self.config.supp_l)
                    f_dict[fval]=[oldIndex,index]
                oldIndex=index
            oldKey=tup
            
        if oldKey:
            n=oldKey.Index-oldIndex+1
            if n>=self.config.supp_l:
                num_f+=1
                #fit(fd[oldIndex:],f,v,n)
                fval=tuple([getattr(oldKey,j) for j in f])
                f_dict[fval]=[oldIndex]
        self.stats.stopTimer('innerloop')
        
        if len(f_dict)<self.config.supp_g:
            if self.config.supp_inf:#if toggle is on
                self.failedf.add(group[:division])
            log.debug("global support threshold not reached for pattern F=%s, V=%s (%d < %d)", f, v, len(f_dict), self.config.supp_g)
            return
        else:
            for fval in f_dict:
                indices=f_dict[fval]
                if len(indices)==2: #indices=[oldIndex,index]
                    fit(fd[indices[0]:indices[1]],f,fval,v,indices[1]-indices[0])
                else: #indices=[oldIndex]
                    fit(fd[indices[0]:],f,fval,v,oldKey.Index-indices[0]+1)
        
        if pattern:
            log.debug("insert local pattern %s", pattern)
            self.stats.startTimer('insertion')
            self.config.conn.execute("INSERT INTO "+self.config.pattern_schema+"."+self.config.table+"_local values"+','.join(pattern))
            self.stats.stopTimer('insertion')
        
        for agg in valid_c_f:
            if agg in sample_invalid and 'c' in sample_invalid[agg]:
                continue
            lamb_c=valid_c_f[agg]/num_f
            if valid_c_f[agg]>=self.config.supp_g and lamb_c>self.config.lamb:
                log.info("found global pattern P = (%s, %s, %s, const)", f, v, agg)
                self.glob.append(self.addGlobal(f,v,agg,'const',self.config.theta_c,lamb_c,
                                                global_dev_pos[agg]['c'],global_dev_neg[agg]['c']))
                self.stats.incr('patterns.global')
            else:
                log.info("global pattern candidate P = (%s, %s, %s, const) does not hold", f, v, agg)
             
        for agg in valid_l_f:
            if agg in sample_invalid and 'l' in sample_invalid[agg]:
                continue
            lamb_l=valid_l_f[agg]/num_f
            if valid_l_f[agg]>=self.config.supp_g and lamb_l>self.config.lamb:
                log.info("found global pattern P = (%s, %s, %s, linear)", f, v, agg)
                self.glob.append(self.addGlobal(f,v,agg,'linear',self.config.theta_l,lamb_l,
                                                global_dev_pos[agg]['l'],global_dev_neg[agg]['l']))
                self.stats.incr('patterns.global')            
            else:
                log.info("global pattern candidate P = (%s, %s, %s, linear) does not hold", f, v, agg)
         
                          
    def addLocal(self,f,f_val,v,agg,model,theta,describe,param,dev_pos,dev_neg):#left here
        f='ARRAY'+str(list(f)).replace('"','')
        f_val='ARRAY'+str([str(val).replace("'","") for val in f_val]).replace('"','')
        v='ARRAY'+str(list(v)).replace('"','')
        agg="'"+agg+"'"
        model="'"+model+"'"
        theta="'"+str(theta)+"'"
        describe="'"+str(describe).replace("'","")+"'"
        return '('+','.join([f,f_val,v,agg,model,theta,describe,str(param),str(dev_pos),str(dev_neg)])+')'
    
    
    def addGlobal(self,f,v,agg,model,theta,lamb,dev_pos,dev_neg):
        f='ARRAY'+str(list(f)).replace('"','')
        v='ARRAY'+str(list(v)).replace('"','')
        agg="'"+agg+"'"
        model="'"+model+"'"
        theta="'"+str(theta)+"'"
        lamb="'"+str(lamb)+"'"
        return '('+','.join([f,v,agg,model,theta,lamb,str(dev_pos),str(dev_neg)])+')'
         
    
    def createTable(self, pattern_schema):
        if self.config.reg_package=='sklearn':
            ptype='varchar'
        else:
            ptype='json'
        
        self.config.conn.execute('CREATE SCHEMA IF NOT EXISTS '+pattern_schema)
        
        self.config.conn.execute('DROP TABLE IF EXISTS '+pattern_schema+'.'+self.config.table+'_local;')    
        self.config.conn.execute('create table IF NOT EXISTS '+pattern_schema+'.'+self.config.table+'_local('+
                     'fixed varchar[],'+
                     'fixed_value varchar[],'+
                     'variable varchar[],'+
                     'agg varchar,'+
                     'model varchar,'+
                     'theta float,'+
                     'stats varchar,'+
                     'param '+ptype+','+
                     'dev_pos float,'+
                     'dev_neg float);')
        
        self.config.conn.execute('DROP TABLE IF EXISTS '+pattern_schema+'.'+self.config.table+'_global')
        self.config.conn.execute('create table IF NOT EXISTS '+pattern_schema+'.'+self.config.table+'_global('+
                     'fixed varchar[],'+
                     'variable varchar[],'+
                     'agg varchar,'+
                     'model varchar,'+
                     'theta float,'+
                     'lambda float, '+
                     'dev_pos float,'+
                     'dev_neg float);')
        
        attr=''
        for key in self.time:
            attr+=key+' varchar,'
        self.config.conn.execute('create table IF NOT EXISTS time_naive('+
                          'id serial primary key,'+
                          attr+
                          'description varchar);')
        log.debug("done creating tables")
        
        
    def insertTime(self,description):
        attributes=list(self.stats.time)
        values=[str(self.stats.time[i]) for i in attributes]
        attributes.append('description')
        values.append(description)
        self.config.conn.execute('INSERT INTO time_detail_fd('+','.join(attributes)+') values('+','.join(values)+')')
