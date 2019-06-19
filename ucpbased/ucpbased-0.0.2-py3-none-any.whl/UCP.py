from ucpbased.UseCasePoints import UseCasePoints
from ucpbased.projectcomplexity.UCP_EFactor import UCP_EFactor
from ucpbased.projectcomplexity.UCP_TFactor import UCP_TFactor
from ucpbased.projectsize.UCP_UAW import UCP_UAW
from ucpbased.projectsize.UCP_UUCW import UCP_UUCW
from ucpbased.projectsize.UnadjustedUseCasePoints import UnadjustedUseCasePoints
from ucpbased.riskfactors.ProductivityFactors import ProductivityFactors


class UCP:

    def __init__(self):
        self.uaw = 0
        self.uucw = 0
        self.uucp = 0
        self.tcf = 0
        self.ecf = 0
        self.ucp = 0

    def input_UAW(self, A1_Assessment, A2_Assessment, A3_Assessment):
        self.uaw = UCP_UAW(A1_Assessment, A2_Assessment, A3_Assessment).getUAW()
        return self.uaw

    def input_UUCW(self, U1_Assessment, U2_Assessment, U3_Assessment):
        self.uucw = UCP_UUCW(U1_Assessment, U2_Assessment, U3_Assessment).getUUCW()
        return self.uucw

    def get_UUCP(self):
        self.uucp = UnadjustedUseCasePoints(self.uaw, self.uucw).getUUCP()
        return self.uucp

    def input_TFactor(self, T1_Assessment, T2_Assessment, T3_Assessment,
                      T4_Assessment, T5_Assessment, T6_Assessment, T7_Assessment,
                      T8_Assessment, T9_Assessment, T10_Assessment,
                      T11_Assessment, T12_Assessment, T13_Assessment):
        self.tcf = UCP_TFactor(T1_Assessment, T2_Assessment, T3_Assessment,
                               T4_Assessment, T5_Assessment, T6_Assessment, T7_Assessment,
                               T8_Assessment, T9_Assessment, T10_Assessment,
                               T11_Assessment, T12_Assessment, T13_Assessment).getTCF()
        return self.tcf

    def input_EFactor(self, E1_Assessment, E2_Assessment, E3_Assessment,
                      E4_Assessment, E5_Assessment, E6_Assessment, E7_Assessment,
                      E8_Assessment):
        self.ecf = UCP_EFactor(E1_Assessment, E2_Assessment, E3_Assessment,
                               E4_Assessment, E5_Assessment, E6_Assessment, E7_Assessment,
                               E8_Assessment).getECF()
        return self.ecf

    def get_UCP(self):
        useCasePoints = UseCasePoints()
        self.uucp = self.uaw + self.uucw
        self.ucp = useCasePoints.UCP(self.uucp, self.tcf, self.ecf)
        return self.ucp

    def get_MH(self, pf):
        productivityFactors = ProductivityFactors(self.ucp, pf)
        mh = productivityFactors.getMH()
        return mh
