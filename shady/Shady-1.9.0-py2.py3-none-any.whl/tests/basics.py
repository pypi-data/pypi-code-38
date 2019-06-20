import Shady
def TestSetup( self ):
	Shady.PixelRuler( self ).visible = lambda t: ( t % 6 ) > 3
	Shady.FrameIntervalGauge( self )
	t = Shady.TearingTest( self )
	t.Set( sigfunc=1, sigf=2. / t.width, siga=5000, outOfRangeColor=-1 )
	return "Please take a video of this screen with your\nphone for five seconds or so, then press Q."
