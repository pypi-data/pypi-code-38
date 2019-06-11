#!/usr/bin/env python3

import sys # print stderr

_DEBUG=0
from math import sin,cos,tan,pi,sqrt,asin,atan
def _REACT( op_amu,op_mex,ot_amu,ot_mex,oo_amu,oo_mex,oor_amu,oor_mex, TKE=21.0, ExcT=0,theta=10.0,silent=0, output="all" ):
        
        if TKE==0:
                print("X...  TKE is zero.... quit")
                quit()
        #print( "D... TKE=",TKE )
        #my (  $exctgt, $amu1, $amu2, $amu3, $amu4, $Q )=@_;

        Q= op_mex+ot_mex - oo_mex - oor_mex # based on mex; notwrk4 e+e-
        Qamu=op_amu+ot_amu-oo_amu-oor_amu   # based on amu
        Q=Qamu*931.49403*1000 # in keV
        # e+e- and gamma case tested on h2+h1 -> he3 + ...

        if _DEBUG==1: print("DEBUG ... Q={}".format(Q) , file=sys.stderr);
        if silent==0:
                #print()
                print("\n--- {:3.1f} deg  TKE={:6.3f} MeV Q={:6.3f} MeV ------------".format(theta,TKE,Q/1000. ) ,  file=sys.stderr )
        #rs;
        m1=op_amu* 931.49403
        m2=ot_amu* 931.49403
        m3=oo_amu* 931.49403
        m4=oor_amu* 931.49403
        t=TKE  # projectile energy
        # adding excitation of target later

        if _DEBUG==1:  print("DEBUG...   AMUs (nudat): %f %f %f %f" % (m1,m2,m3,m4) , file=sys.stderr)
        es=t + m1  + m2;
        ##### JAROCMS p1 good; E1 ^2=(t + m1)**2  ####
        p1=sqrt(     (t + m1)**2  - m1**2  )
        ######### JAROCMS Ecms  from invariant # p3cform= sum p^2/2m
        Ecms2= (t + m1)**2   +  m2**2  + 2*(t + m1)*m2 - p1**2
        Ecms=sqrt( Ecms2 )
        TKEcms=Ecms-m1-m2
        if _DEBUG!=0:  print("DEBUG... TKEcms=",TKEcms, file=sys.stderr)

        # theta is defacto theta3.
        costh3=cos( theta * 3.1415926535/180);
        sinth3=sin( theta * 3.1415926535/180);
        INVALID=0;

        if (ExcT>0.0) and (_DEBUG!=0): print("DEBUG excitation=", ExcT,"MeV", file=sys.stderr)
        m4=m4 + ExcT #adding excitation of target HERE

        #nerelativ
        #    $m3=$m3 + $exctgt; #adding excitation of scattered particle HERE
        #    my $SQne=sqrt( $m1*$m3*$t*$costh3**2 +($m1+$m2)*($m4*$Q+($m4-$m1)*$t)  );
        #    my $t3na=(sqrt($m1*$m3*t)*$costh3 + $SQne )**2 /($m1+$m2)**2;
        #    my $t3nb=(sqrt($m1*$m3*t)*$costh3 - $SQne )**2 /($m1+$m2)**2;
        #    print "Q=$Q ;  T3nerel = $t3na  $t3nb  \n";
        #-->>    print "               Q=$Q , p=$p1;  \n";
        #relativ
        a3b= es**2 - p1**2 + ( m3**2 - (m4)**2)
        #--- this is square root  from eq (4)  T3=.......
        SQ= a3b**2 - 4*m3**2 * (es**2-p1**2*costh3**2)
        #    print  $a3b," ",$m3," ",$es,"  ",$p1,"  ",$costh3,"\n";
        #    print  $a3b**2,"    ", 4*$m3**2 * ($es**2-($p1**2)*($costh3**2) ) ,"\n";
        if ( SQ<0 ):
                print("    SQ < 0  : ",SQ,"  : setting to           ##### ZERO ####")
                SQ=0
                INVALID=1
                print("!... probably under threshold, quitting")
                return

        SQ=sqrt( SQ ) # prepare for sqrt   <0
        ####### 2 SOLUTIONS ########
        t3a=( a3b * es + p1* costh3* SQ)/2/( es**2 - p1**2* costh3**2) - m3
        t3b=( a3b * es - p1* costh3* SQ)/2/( es**2 - p1**2* costh3**2) - m3
        ####### 2 SOLUTIONS ########
        if _DEBUG!=0: print("DEBUG...    kinetic E T3={} ({}) \n".format(t3a,t3b) , file=sys.stderr);


        # prepare 2-solution's --- decision......
        E1=t+m1 # full energy
        V=p1/( E1 + m2 ) # CMS velocity  pc/E->v/c?
        ttr=- ( m1 + m2)/ m2 * Q
        if (Q>0):
                ttr=0
        ttrc=-Q
        if (Q>0):
                ttrc=0
        if _DEBUG!=0: print("DEBUG...    E1={}  V={} t={} ttr={}\n".format( E1, V, t,ttr) , file=sys.stderr);


        # equation   (21)  p3c CMS
        # !!!!!!!!!!  error in this line - use p3c defined later!!!!!
        #
        # 20171107 - i commentout
        #p3c= m2*sqrt( (t-ttr)*(t-ttr + 2/m2*m3*m4 )/( 2*m2*t + (m1+m2)**2)  )
        # varianta p3c: (19) and (20)
        Es=t + m1 +m2
        Esc= Es * sqrt( 1-V**2 )
        if _DEBUG!=0: print('DEBUG ... Es,Esc',Es,Esc,  file=sys.stderr)
        #PROB  print "tot E= $Es  totEcms = $Esc   p3c= $p3c\n";
        p3c=sqrt( ( Esc**2-( m3+ m4)**2)*( Esc**2-( m3- m4)**2) )/2/Esc
        #PROB  print "tot E= $Es  totEcms = $Esc   p3c= $p3c\n";

        E3c=sqrt( p3c**2 + m3**2 )
        
        #print("D.... p3c  E3c ",p3c, E3c)
        rho3=V/p3c * E3c
        #    mam-li  p3c  mam samozrejme i p4c :)
        #  ziskam E4c - bude dobre pro theta4
        p4c=p3c

        E4c=sqrt ( p4c**2 + m4**2 )
        # Q !!!! IN KEV !!!!!! from the database
        t4a= t- t3a + Q/1000; #rovnice (1) zzEne, nezavisle
        if _DEBUG:print("... DEBUG: {}  {}  {}".format(t,t3a,Q)  , file=sys.stderr)
        t4b= t- t3b + Q/1000; #rovnice (1) zzEne, nezavisle


        #======================================================== THETA3
                        #ziskej p3 (pozor na <0) klasicky ze znalosti p a t  [p3b]
        p3=    ( t3a +  m3)**2  -  m3**2  ;  # sqrt pozdeji...
        p4=    ( t4a +  m4)**2  -  m4**2  ;  # sqrt pozdeji...
        p4b=   ( t4b +  m4)**2  -  m4**2  ;  # sqrt pozdeji...i added 20180830
        p3b=   ( t3b +  m3)**2  -  m3**2  ;  # sqrt pozdeji...
        if (p3<0):
                print("    p3 <0:  $p3 : setting to ##### ZERO ####")
                p3=0.0
        p3=sqrt(  p3  )
        if (p3b<0):
                print("    p3b <0:  $p3b : setting to ##### ZERO ####")
                p3b=0.0

        p3b=sqrt(  p3b  )
        # symetrically for p4: - it was missing in beta4
        if (p4<0):
                print("    p4 <0:  $p4 : setting to ##### ZERO ####")
                p4=0.0
        p4=sqrt(  p4  )
        if (p4b<0):
                print("    p4b <0:  $p4b : setting to ##### ZERO ####")
                p4b=0.0

        p4b=sqrt(  p4b  )


        #    $p3b=42.85920142;
        # ziskej plnou informaci o  theta3cm - i sin i cos =>  theta3cm a  PI-theta3cm
        # equation (22) 2nd part
        sinth3cm = p3/ p3c* sinth3
        sinth3cmb= p3b/p3c* sinth3
        costh3cm=  ( p3*  costh3)/(1/sqrt(1-V**2))
        costh3cmb= ( p3b* costh3)/(1/sqrt(1-V**2))

        costh3cm= ( costh3cm -  V*E3c )/ p3c
        costh3cmb=( costh3cm -  V*E3c )/ p3c
#		tmpr2dc=R2dc
#		R2dc=1.0   ####  change default transofrmation..........

        th3cm = asin(  sinth3cm )*180/3.1415926
        th3cmb= asin(  sinth3cmb)*180/3.1415926
        if (costh3cm <0):
                th3cm =180-th3cm
        if (costh3cmb<0):
                th3cmb=180-th3cmb
        #-====================================================== THETA4
        th4cm =  180.0 - th3cm
        th4cmb=  180.0 - th3cmb
        #z eq (22)
        cotgth4 = 1/(sqrt(1-V**2)) *  ( p4c*cos( th4cm /180 * 3.1415926) + V*E4c  )
        cotgth4b= 1/(sqrt(1-V**2)) *  ( p4c*cos( th4cmb/180 * 3.1415926) + V*E4c  )
        tmpjmen =( p4c* sin( th4cm/180.0 * 3.1415926 )  )
        tmpjmenb=( p4c* sin( th4cmb/180.0 * 3.1415926 ) )
        if ( tmpjmen ==0):
                print(" ?...   p4csin ==0::cotg is taken only approximate", file=sys.stderr)
                #print("o...   p4csin ==0:  $tmpjmen :cotg approx: setting to ##### ZERO ####")
                cotgth4=1e+7
        else:
                cotgth4= cotgth4/tmpjmen
        if ( tmpjmenb==0):
                print("o...    p4csinb ==0:::cotg approximate: \n", file=sys.stderr)
#                print("o...    p4csinb ==0:  $tmpjmenb :cotg approx: setting to ##### ZERO ####\n")
                cotgth4b=1e+7
        else:
                cotgth4b= cotgth4b/tmpjmenb

        theta4= atan( 1/ cotgth4 )*180/3.1415926
        if (theta4<0):
                theta4=180+theta4
        theta4b=atan( 1/ cotgth4b )*180/3.1415926
        if (theta4b<0):
                theta4b=180+theta4b


        # equation (32)  theta max
        #    print "doing sinmax\n";
        theta3max=180.0
        if (rho3>=1.00000):
                sinth3max=sqrt(  (1-V**2)/(rho3**2-V**2)  )
                theta3max=asin( sinth3max )*180/3.1415926
        else:
                theta3max=180.0
                t3b=0.0
#		R2dc=tmpr2dc  #put back translation deg2rad.......................

        # equation (30) for conversion sigma cm -> sigma lab (sCMS=K*sLab)
        #    my $convsig=($p3c/$p3) * sqrt( 1- (($rho3**2-$V**2)*$sinth3**2)/(1-$V**2)  );
        #    print "doing  k sigma  V=$V\n";
        #
        #   at 0 or 180 == p3c/p3
        convsig=  (( rho3**2-V**2)*sinth3**2)/(1-V**2)
        convsig=1.0 - convsig
        if (convsig>0 and p3>0):
                convsig=(p3c/p3)**2 * sqrt(  convsig )
        else:
                convsig=0.

        # b-variant
        convsigb=  ((rho3**2-V**2)*sinth3**2)/(1-V**2)
        convsigb=1.0 - convsigb
        if (convsigb>0 and p3b>0):
                convsigb=(p3c/p3b)**2 * sqrt(  convsigb )
        else:
                convsigb=0.


        #=====================  INVALIDATE ALL ====================
        if (INVALID==1):
                (th3cm,th4cm,theta4,t3a,t4a,th3cmb,th4cmb,theta4b,t3b,t4b  )=(   0,   0,     0,      0,    0,   0,     0,      0,       0,    0 )

        p3cform=0 # case of gamma
        if _DEBUG:print("DEBUG:  {}   {}  {}".format(m3,m4, p3cform) , file=sys.stderr)
        if (m3>0):
                p3cform=(p3c**2)/2/m3
        if _DEBUG:print("DEBUG:  {}   {}  {}".format(m3,m4, p3cform) , file=sys.stderr)
        if (m4>0):
                p3cform=p3cform+(p4c**2)/2/m4
        if _DEBUG:print("DEBUG:  {}   {}  {}".format(m3,m4, p3cform) , file=sys.stderr)

        #===== calculation to here:
        if not (rho3>1):
                th3cmb=0.
                th4cmb=0.
                t3b=0. 
        #ttr/1000
        #ttrc/1000
        #Q/1000
        E3full=sqrt(p3**2 + m3**2 )
        gamma3=E3full/m3
        gamma1,beta1,beta3,gamma4,beta4=0,1,1,0,1
        Kscsl= convsig # factor
        Kscslb= convsigb # factor
        if gamma3>1:
                    E1full=E1
                    gamma1=E1full/m1
                    beta1=sqrt( 1- (1/gamma1/gamma1) )
                    #print("        beta1={:15.5f}    {:.1f}mm/ns".format( beta1 , beta1*300 )   )

                    beta3=sqrt( 1- (1/gamma3/gamma3) )
                    #print("        beta3={:15.5f}    {:.1f}mm/ns".format( beta3 , beta3*300 )   )

                    E4full=sqrt(p4**2 + m4**2 )
                    if m4==0:
                            gamma4=0.
                            beta4=1.
                    else:
                            gamma4=E4full/m4
                            beta4=sqrt( 1- (1/gamma4/gamma4) )
                    #print("        beta4={:15.5f}    {:.1f}mm/ns".format( beta4 , beta4*300 )   )

        Q=Q/1000 # Q in MeV
        ttr=ttr/1000 #threshold lab in MeV
        ttrc=ttrc/1000 # threshold cms in MeV
        if (silent==0) and (output=="all"):  ############################### PRINTOUT #####
#                print(' ')
#                print("        T1   =%15.5f  (projectile TKE)" % t )
                #         printf ("        th3MX=%15.5f\n",$theta3max );
#                print( "       th3  =%15.5f  (thetaMAX=%15.5f)" %  (theta,  theta3max)  )
#                print("----------------------------------")
                print("        th3cm=%15.5f" % th3cm )
                print("        th4cm=%15.5f" % th4cm )
                print("        th4  =%15.5f" % theta4 )
                print("        T3a  ={:15.5f}       T4b{:15.5f}  ".format( t3a, t3b ) )
                print("        T4a  ={:15.5f}       T4b{:15.5f}  ".format( t4a, t4b ) )
                print("        Kscsl=%15.5f (sigma_cms=Kscsl*sigma_lab)" % convsig )
                print("        rho3 =%15.5f (if <=1.0 : 1 solution else 2 solutions for T3)" %  rho3 )

                if (rho3>1):
                        print("     b  th3cm=%15.5f" % th3cmb )
                        print("     b  th4cm=%15.5f" % th4cmb )
                        print("     b  th4  =%15.5f" % theta4b )
                        print("     b  T3(b)=%15.5f" % t3b)
                        print("     b  T4(b)=%15.5f" % t4b )
                        print("     b Kscslb=%15.5f sigma_cms=K*sigma_lab)" % convsigb )
#                else:
#                        th3cmb=0.
#                        th4cmb=0.
#                        t3b=0.

                print("        p1   =%15.5f (projectile momentum)" %  p1 )
                #print("        E1   =%15.5f (projectile - total energy)" % E1 )
                print("        V    =%15.5f (velocity of CMS ... v/c)" % V )
                print("        ttr  ={:15.5f} (Threshold in Lab)".format(ttr) )
                print("        ttrc ={:15.5f} (Threshold in CMS == -Q)".format(ttrc) )
                print("        Q    ={:15.5f} (if Q>0 = exoterm  [MeV])".format(Q) )
                print("        ExcT=%15.5f (input tgt excitation)" % ExcT )
                print("        p3c  =%15.5f"  % p3c )
                print("        p4c  =%15.5f"  % p4c )
                print(" TKECMS(1,2) =%15.5f"  %  TKEcms )
                print("EtotCMS(3,4) =%15.5f"  %  p3cform )
                #                              print "total Ek =  ",($p3c**2)/2/$m3+($p4c**2)/2/$m4 , "\n";
                print("        p3   ={:15.5f}     b  p3b  ={:15.5f}".format(p3,p3b) )
                print("        p4   ={:15.5f}     b  p4b  ={:15.5f}".format(p4,p4b) )
                ###print("        E3c  ={:15.5f}     ".format( E3c) )
                #E3full=sqrt(p3**2 + m3**2 )
                ###print("        E3   ={:15.5f}      (p3^2+m3^2)^1/2".format( E3full ) )
                #gamma3=E3full/m3
                ###gamma3=1.00125  # TKE= (gamma3-1)*m3
                ###print("       gamma3={:15.5f}      (E3/m3)".format( gamma3  ) )
                if gamma3>1:
                    #E1full=E1
                    #gamma1=E1full/m1
                    #beta1=sqrt( 1- (1/gamma1/gamma1) )
                    print("        beta1={:15.5f}    {:.1f}mm/ns".format( beta1 , beta1*300 )   )

                    #beta3=sqrt( 1- (1/gamma3/gamma3) )
                    print("        beta3={:15.5f}    {:.1f}mm/ns".format( beta3 , beta3*300 )   )

                    #E4full=sqrt(p4**2 + m4**2 )
                    #if m4==0:
                    #        gamma4=0.
                    #        beta4=1.
                    #else:
                    #        gamma4=E4full/m4
                    #        beta4=sqrt( 1- (1/gamma4/gamma4) )
                    print("        beta4={:15.5f}    {:.1f}mm/ns".format( beta4 , beta4*300 )   )

                    # E2full=m2
                    # gamma2=E2full/m2
                    # beta2=sqrt( 1- (1/gamma2/gamma2) )
                    # print("        beta2={:15.5f}    {:.1f}mm/ns".format( beta2 , beta2*300 )   )

                #print("        E4c  =%15.5f" % E4c )

                #    my $t4a=($a4*$es + $p1*$costh4* $SQ)/2/($es**2 - $p1**2*$costh4**2) - $m3;
                #    my $t4b=($a4*$es + $p1*$costh4* $SQ)/2/($es**2 - $p1**2*$costh4**2) - $m3;
                #    print "  $a3b = A3 ;  $t3a = T3A ;   $t3b = T3B \n";
                if (rho3>1):
                        print("        t3a =%15.5f   and  t3b  %f  (TKE)" % (t3a,t3b)  )
                else:
                        print("   TKEout t3a =%15.5f  " % t3a )
                #    print "    kinetic E T4=$t4a ($t4b) \n";


        rs=t3a;
        #####################################################
        #
        # RETURN HERE ====================================
        #
        ##################################################

#        return t3a,t3b,th3cm,th3cmb,  p3cform  ,convsig
##################################
#  RETURN FROM REACTION
#       i need also TKE_CMS and ANGLE_CMS FOR RUTHERFORD
#              th3cm  ... OK
#              TKEcms ... OK   so it already is OK
#              0,1       2,3            4,     5
        if output!="all":
                #====== output can have  LIST from NOW ON
                output=output.split(',')
                if len(output)>1:
                        print("H...  from bash-you can get the array vals: my_array=( $(<command>) )", file=sys.stderr)
                        print("H...      read with   echo  ${#my_array[@]}  ${my_array[0]}   ", file=sys.stderr)
                print( output,"= ", file=sys.stderr )
                ret=""
                for i in output:
                        try:
                                ret+= str( locals()[i] ) +"\n"
                        except:
                                print("X... NO variable like",i)
                                ret+="0\n"
                ret=ret.rstrip()
                #print( ret) # NO PRINT
                return ret  #=================================++ RETURN when not ALL
                print( locals()[output] )
                return locals()[output]
        #print("D...  old return")# old tpe return
        return t3a,t3b,th3cm,th3cmb,  TKEcms  ,convsig
        #print("   Kscsl=%15.5f (sigma_cms=K*sigma_lab)" % convsig )
        #print("b  Kscsl=%15.5f sigma_cms=K*sigma_lab)" % convsigb )

        # self.T3       =t3a
        # self.T3b      =t3b
        # self.Theta3   =theta
        # self.Theta3cms   =th3cm
        # self.Theta3cmsb  =th3cmb
        # #self.Theta3b   =thetab
        # self.Theta3max=theta3max
        # self.Theta4   =theta4
        # self.Theta4b  =theta4b
        # self.Ecms     =p3cform
        # self.Kscsl    =convsig
        # self.Kscslb   =convsigb
        # self.Q        =Q
        # self.Vc       =V


        # self.pd1_Ang=pd.DataFrame( [ [theta, None, theta3max, th3cm, th3cmb ],[ theta4,  theta4b, None, th4cm, th4cmb ]  ],
        #         index=['part3 '+str(oo)+':','part4 '+str(oor)+':'],
        #         columns=[ 'Theta_LAB', 'Th_LAB_b','Th_LAB_max','Th_CMS','Th_CMS_b'] )
        # #print(self.pd1_ang)
        # #print(' ')

        # self.pd2_Tke=pd.DataFrame( [ [ t, t3a, t3b, t4a,t4b  ]   ],  index=['Energies: '],
        #         columns=[ 'T1', 'T3_a', 'T3_b', 'T4_a','T4_b'] )
        # #print(self.pd2_T)
        # #print(' ')

        # self.pd3_Ene=pd.DataFrame( [ [ Q, ttr, ttrc , p3cform , ot.Exc]   ],  index=['Energies: '],
        #         columns=[ 'Q','ThrLAB','ThrCMS', 'EtotCMS', 'ExcTgt'] )
        # #print(self.pd3_Ene)
        # #print(' ')

        # self.pd4_Ep=pd.DataFrame( [ [E1, p1, None, None , None],[ None, p3, E3c, p3c , p3b ] , [ None, None, E4c, p4c , None ]  ],
        #         index=['part1 '+str(op)+':',
        #                 'part3 '+str(oo)+':',
        #                 'part4 '+str(oor)+':',
        #                 ],
        #         columns=[ 'E_LAB', 'p_LAB','E_CMS','p_CMS' , 'p_b_CMS'] )

        # self.pd5_Trans=pd.DataFrame( [ [ convsig, convsigb, rho3, V ] ],
        #         index=['Conversions :' ],
        #         columns=[ 'XScms2lab', 'XScms2labb','rho3','Vcms' ] )

        #print "           try  http://t2.lanl.gov/data/qtool.html for all possible reactions\n";







        


################################################
#  this is called from nuphy.py
################################################
# this needs NuPhyPy.db.ReadNubase.isotope library
def react( a,b,  c,d, TKE=1, theta=10, ExcT=0 , silent=0, output="all"):
    zok=a.Z+b.Z-c.Z-d.Z==0
    aok=a.A+b.A-c.A-d.A==0
    if not zok:
        print("Z sum incorrect:  particle 4 Z=",a.Z+b.Z-c.Z,"!=", d.Z)
        return [0,0,0,0,0,0,0,0] # why I added also here?
    if not aok:
        print("A sum incorrect:  particle 4 A=",a.A+b.A-c.A)
        return [0,0,0,0,0,0,0,0]
    if not zok:
        return [0,0,0,0,0,0,0,0]

    #print(  a.amu, a.mex, b.amu, b.mex, c.amu, c.mex, d.amu, d.mex ,"\n============")
    res=_REACT( a.amu, a.mex, b.amu, b.mex,
            c.amu, c.mex, d.amu, d.mex,
                TKE=TKE, theta=theta, ExcT=ExcT,silent=silent, output=output)
    return res



print("i... module  kinematics  is being loaded", file=sys.stderr)
    
if __name__ == "__main__":

    print("running kinematics.py as main, 3he+16o @ 25MeV")

    r=_REACT( 3.01602931959, 14931.2155,
              15.9949146198, -4737.0013,
              3.01602931959, 14931.2155,
              15.9949146198, -4737.0013,
              TKE=24.96,
           theta=10.0  )
    r=_REACT( 1.008, 7288.97,
              15.9949146198, -4737.0013,
              1.008, 7288.97,
              15.9949146198, -4737.0013,
              TKE=1.175,
           theta=10.0  ) # beta==0.05 gamma 1.00125
    print(r)
