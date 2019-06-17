class Quote:
    _askPrice = [0.0]*10
    _askVolume = [0]*10
    _bidPrice = [0.0]*10
    _bidVolume = [0]*10

    def __init__(self):
        pass

    @property
    def AskPrice(self):
        return self._askPrice

    @property
    def AskVolume(self):
        return self._askVolume

    @property
    def BidPrice(self):
        return self._bidPrice

    @property
    def BidVolume(self):
        return self._bidVolume

    @property
    def AskPrice1(self):
        return self.AskPrice[0]
      
    @AskPrice1.setter
    def AskPrice1(self,value):
        self.AskPrice[0] = value
      
    @property
    def AskPrice2(self):
        return self.AskPrice[1]
      
    @AskPrice2.setter
    def AskPrice2(self,value):
        self.AskPrice[1] = value
        
    @property
    def AskPrice3(self):
        return self.AskPrice[2]
      
    @AskPrice3.setter
    def AskPrice3(self,value):
        self.AskPrice[2] = value

                
    @property
    def AskPrice4(self):
        return self.AskPrice[3]
      
    @AskPrice4.setter
    def AskPrice4(self,value):
        self.AskPrice[3] = value
                
    @property
    def AskPrice5(self):
        return self.AskPrice[4]
      
    @AskPrice5.setter
    def AskPrice5(self,value):
        self.AskPrice[4] = value
                
    @property
    def AskPrice6(self):
        return self.AskPrice[5]
      
    @AskPrice6.setter
    def AskPrice6(self,value):
        self.AskPrice[5] = value
                
    @property
    def AskPrice7(self):
        return self.AskPrice[6]
      
    @AskPrice7.setter
    def AskPrice7(self,value):
        self.AskPrice[6] = value
                
    @property
    def AskPrice8(self):
        return self.AskPrice[7]
      
    @AskPrice8.setter
    def AskPrice8(self,value):
        self.AskPrice[7] = value
                
    @property
    def AskPrice9(self):
        return self.AskPrice[8]
      
    @AskPrice9.setter
    def AskPrice9(self,value):
        self.AskPrice[8] = value
                
    @property
    def AskPrice10(self):
        return self.AskPrice[9]
      
    @AskPrice10.setter
    def AskPrice10(self,value):
        self.AskPrice[9] = value
                
    @property
    def AskVolume1(self):
        return self.AskVolume[0]
      
    @AskVolume1.setter
    def AskVolume1(self,value):
        self.AskVolume[0] = value
                
    @property
    def AskVolume2(self):
        return self.AskVolume[1]
      
    @AskVolume2.setter
    def AskVolume2(self,value):
        self.AskVolume[1] = value
                
    @property
    def AskVolume3(self):
        return self.AskVolume[2]
      
    @AskVolume3.setter
    def AskVolume3(self,value):
        self.AskVolume[2] = value
                
    @property
    def AskVolume4(self):
        return self.AskVolume[3]
      
    @AskVolume4.setter
    def AskVolume4(self,value):
        self.AskVolume[3] = value
                
    @property
    def AskVolume5(self):
        return self.AskVolume[4]
      
    @AskVolume5.setter
    def AskVolume5(self,value):
        self.AskVolume[4] = value
                
    @property
    def AskVolume6(self):
        return self.AskVolume[5]
      
    @AskVolume6.setter
    def AskVolume6(self,value):
        self.AskVolume[5] = value
                
    @property
    def AskVolume7(self):
        return self.AskVolume[6]
      
    @AskVolume7.setter
    def AskVolume7(self,value):
        self.AskVolume[6] = value
                
    @property
    def AskVolume8(self):
        return self.AskVolume[7]
      
    @AskVolume8.setter
    def AskVolume8(self,value):
        self.AskVolume[7] = value
                
    @property
    def AskVolume9(self):
        return self.AskVolume[8]
      
    @AskVolume9.setter
    def AskVolume9(self,value):
        self.AskVolume[8] = value
                
    @property
    def AskVolume10(self):
        return self.AskVolume[9]
      
    @AskVolume10.setter
    def AskVolume10(self,value):
        self.AskVolume[9] = value
                
    @property
    def BidPrice1(self):
        return self.BidPrice[0]
      
    @BidPrice1.setter
    def BidPrice1(self,value):
        self.BidPrice[0] = value
                
    @property
    def BidPrice2(self):
        return self.BidPrice[1]
      
    @BidPrice2.setter
    def BidPrice2(self,value):
        self.BidPrice[1] = value
                
    @property
    def BidPrice3(self):
        return self.BidPrice[2]
      
    @BidPrice3.setter
    def BidPrice3(self,value):
        self.BidPrice[2] = value
                
    @property
    def BidPrice4(self):
        return self.BidPrice[3]
      
    @BidPrice4.setter
    def BidPrice4(self,value):
        self.BidPrice[3] = value
                
    @property
    def BidPrice5(self):
        return self.BidPrice[4]
      
    @BidPrice5.setter
    def BidPrice5(self,value):
        self.BidPrice[4] = value
                
    @property
    def BidPrice6(self):
        return self.BidPrice[5]
      
    @BidPrice6.setter
    def BidPrice6(self,value):
        self.BidPrice[5] = value
                
    @property
    def BidPrice7(self):
        return self.BidPrice[6]
      
    @BidPrice7.setter
    def BidPrice7(self,value):
        self.BidPrice[6] = value
                
    @property
    def BidPrice8(self):
        return self.BidPrice[7]
      
    @BidPrice8.setter
    def BidPrice8(self,value):
        self.BidPrice[7] = value
                
    @property
    def BidPrice9(self):
        return self.BidPrice[8]
      
    @BidPrice9.setter
    def BidPrice9(self,value):
        self.BidPrice[8] = value
                
    @property
    def BidPrice10(self):
        return self.BidPrice[9]
      
    @BidPrice10.setter
    def BidPrice10(self,value):
        self.BidPrice[9] = value
                
    @property
    def BidVolume1(self):
        return self.BidVolume[0]
      
    @BidVolume1.setter
    def BidVolume1(self,value):
        self.BidVolume[0] = value
                
    @property
    def BidVolume2(self):
        return self.BidVolume[1]
      
    @BidVolume2.setter
    def BidVolume2(self,value):
        self.BidVolume[1] = value
                
    @property
    def BidVolume3(self):
        return self.BidVolume[2]
      
    @BidVolume3.setter
    def BidVolume3(self,value):
        self.BidVolume[2] = value
                
    @property
    def BidVolume4(self):
        return self.BidVolume[3]
      
    @BidVolume4.setter
    def BidVolume4(self,value):
        self.BidVolume[3] = value
                
    @property
    def BidVolume5(self):
        return self.BidVolume[4]
      
    @BidVolume5.setter
    def BidVolume5(self,value):
        self.BidVolume[4] = value
                
    @property
    def BidVolume6(self):
        return self.BidVolume[5]
      
    @BidVolume6.setter
    def BidVolume6(self,value):
        self.BidVolume[5] = value
                
    @property
    def BidVolume7(self):
        return self.BidVolume[6]
      
    @BidVolume7.setter
    def BidVolume7(self,value):
        self.BidVolume[6] = value
                
    @property
    def BidVolume8(self):
        return self.BidVolume[7]
      
    @BidVolume8.setter
    def BidVolume8(self,value):
        self.BidVolume[7] = value
                
    @property
    def BidVolume9(self):
        return self.BidVolume[8]
      
    @BidVolume9.setter
    def BidVolume9(self,value):
        self.BidVolume[8] = value
                
    @property
    def BidVolume10(self):
        return self.BidVolume[9]
      
    @BidVolume10.setter
    def BidVolume10(self,value):
        self.BidVolume[9] = value
        
  