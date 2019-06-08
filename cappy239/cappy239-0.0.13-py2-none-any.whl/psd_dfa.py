# ------------------------------------------------------------------------
# Plota_Versao_2_SERIE_PSD_DFA.pyplot
# ------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy import stats, optimize
import numpy as np
import math

__author__ = 'Paulo Giovani'
__copyright__ = 'Copyright 2017, 3DBMO Project INPE'
__credits__ = ['Paulo Giovani', 'Reinaldo Roberto Rosa', 'Murilo da Silva Dantas']
__license__ = 'GPL'
__version__ = '0.1B'
__maintainer__ = 'Paulo Giovani'
__email__ = 'pg_faria@yahoo.com.br'

#---------------------------------------------------------------------
# Calcula o PSD da série temporal
#---------------------------------------------------------------------
def psd(data):
	"""Calcula o PSD de uma série temporal."""
	
	# Define um intervalo para realizar o ajuste da reta
	INICIO = 10
	FIM = 800
	
	# O vetor com o tempo é o tamanho do número de pontos
	N = len(data)
	tempo = np.arange(len(data))

	# Define a frequência de amostragem
	dt = (tempo[-1] - tempo[0] / (N - 1))
	fs = 1 / dt

	# Calcula o PSD utilizando o MLAB
	power, freqs = mlab.psd(data, Fs = fs, NFFT = N, scale_by_freq = False)

	# Calcula a porcentagem de pontos utilizados na reta de ajuste
	totalFrequencias = len(freqs)
	totalPSD = FIM - INICIO
	porcentagemPSD = int(100 * totalPSD / totalFrequencias)

	# Seleciona os dados dentro do intervalo de seleção
	xdata = freqs[INICIO:FIM]
	ydata = power[INICIO:FIM]

	# Simula o erro
	yerr = 0.2 * ydata

	# Define uma função para calcular a Lei de Potência
	powerlaw = lambda x, amp, index: amp * (x**index)

	# Converte os dados para o formato LOG
	logx = np.log10(xdata)
	logy = np.log10(ydata)

	# Define a função para realizar o ajuste
	fitfunc = lambda p, x: p[0] + p[1] * x
	errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err    
	logyerr = yerr / ydata

	# Calcula a reta de ajuste
	pinit = [1.0, -1.0]
	out = optimize.leastsq(errfunc, pinit, args = (logx, logy, logyerr), full_output = 1)    
	pfinal = out[0]
	covar = out[1]
	index = pfinal[1]
	amp = 10.0 ** pfinal[0]
	indexErr = np.sqrt(covar[0][0])
	ampErr = np.sqrt(covar[1][1]) * amp
	
	# Retorna os valores obtidos
	return freqs, power, xdata, ydata, amp, index, powerlaw, INICIO, FIM
	
#---------------------------------------------------------------------
# Calcula o DFA 1D da série temporal
#---------------------------------------------------------------------
def dfa1d(timeSeries, grau):
	"""Calcula o DFA 1D (adaptado de Physionet), onde a escala cresce
	de acordo com a variável 'Boxratio'. Retorna o array 'vetoutput', 
	onde a primeira coluna é o log da escala S e a segunda coluna é o
	log da função de flutuação."""

	# 1. A série temporal {Xk} com k = 1, ..., N é integrada na chamada função perfil Y(k)
	x = np.mean(timeSeries)
	timeSeries = timeSeries - x
	yk = np.cumsum(timeSeries)
	tam = len(timeSeries)

	# 2. A série (ou perfil) Y(k) é dividida em N intervalos não sobrepostos de tamanho S
	sf = np.ceil(tam / 4).astype(np.int)
	boxratio = np.power(2.0, 1.0 / 8.0)
	vetoutput = np.zeros(shape = (1,2))

	s = 4
	while s <= sf:        
		serie = yk        
		if np.mod(tam, s) != 0:
			l = s * int(np.trunc(tam/s))
			serie = yk[0:l]			
		t = np.arange(s, len(serie), s)
		v = np.array(np.array_split(serie, t))
		l = len(v)
		x = np.arange(1, s + 1)
		
		# 3. Calcula-se a variância para cada segmento v = 1,…, n_s:
		p = np.polynomial.polynomial.polyfit(x, v.T, grau)
		yfit = np.polynomial.polynomial.polyval(x, p)
		vetvar = np.var(v - yfit)
		
		# 4. Calcula-se a função de flutuação DFA como a média das variâncias de cada intervalo
		fs = np.sqrt(np.mean(vetvar))
		vetoutput = np.vstack((vetoutput,[s, fs]))
		
		# A escala S cresce numa série geométrica
		s = np.ceil(s * boxratio).astype(np.int)

	# Array com o log da escala S e o log da função de flutuação   
	vetoutput = np.log10(vetoutput[1::1,:])

	# Separa as colunas do vetor 'vetoutput'
	x = vetoutput[:,0]
	y = vetoutput[:,1]

	# Regressão linear
	slope, intercept, _, _, _ = stats.linregress(x, y)

	# Calcula a reta de inclinação
	predict_y = intercept + slope * x

	# Calcula o erro
	pred_error = y - predict_y

	# Retorna o valor do ALFA, o vetor 'vetoutput', os vetores X e Y,
	# o vetor com os valores da reta de inclinação e o vetor de erros
	return slope, vetoutput, x, y, predict_y, pred_error

#---------------------------------------------------------------------
# Trecho principal
#---------------------------------------------------------------------
def main_psd(df):
	"""Função com o código princiapl do programa."""
	
	print("\nData Analysis for 3DBMO simulations...\n")
	
	# Desabilita as mensagens de erro do Numpy (warnings)
	old_settings = np.seterr(divide = 'ignore', invalid = 'ignore', over = 'ignore')
	
	# Carrega o arquivo de dados
	nomeArquivo = 's8.txt'		
	# data = np.genfromtxt(nomeArquivo,
    #                      delimiter = ',',
    #                      dtype = 'float32',
    #                      filling_values = 0)
	data = df
	
	# Exibe os primeiro N valores do arquivo
	N = 10
	print("Original time series data (%d points): \n" %(len(data)))
	print("First %d points: %s\n" %(N, data[0:10]))
	print()
	
	#-----------------------------------------------------------------
    # Parâmetros gerais de plotagem
    #-----------------------------------------------------------------
	
	# Define os subplots
	fig = plt.figure()
	fig.subplots_adjust(hspace = .3, wspace = .2)
	
	# Tamanho das fontes
	tamanhoFonteEixoX = 16
	tamanhoFonteEixoY = 16
	tamanhoFonteTitulo = 16
	tamanhoFontePrincipal = 25
	
	# Título principal
	tituloPrincipal = '3DBMO Time Series Analysis' 	
	
	#-----------------------------------------------------------------
    # Plotagem da série original
    #-----------------------------------------------------------------
	
	# Define as cores da plotagem
	corSerieOriginal = 'r'
	
	# Título dos eixos da série original
	textoEixoX = 'Tempo'
	textoEixoY = 'Amplitude'
	textoTituloOriginal = 'Original Time Series Data'
	
	print("1. Plotting time series data...")
	
	# Plotagem da série de dados    
	#O = fig.add_subplot(1, 3, 1)    
	O = fig.add_subplot(2, 1, 1)
	O.plot(data, '-', color = corSerieOriginal)
	O.set_title(textoTituloOriginal, fontsize = tamanhoFonteTitulo)
	O.set_xlabel(textoEixoX, fontsize = tamanhoFonteEixoX)
	O.set_ylabel(textoEixoY, fontsize = tamanhoFonteEixoY)
	O.ticklabel_format(style = 'sci', axis = 'x', scilimits = (0,0))
	O.grid()
	
	#-----------------------------------------------------------------
    # Cálculo e plotagem do PSD
    #-----------------------------------------------------------------
	
	# Calcula o PSD
	freqs, power, xdata, ydata, amp, index, powerlaw, INICIO, FIM = psd(data)

	# O valor do beta equivale ao index
	b = index

	# Define as cores da plotagem
	corPSD1 = 'k'
	corPSD2 = 'navy'

	# Título dos eixos do PSD
	textoPSDX = 'Frequência (Hz)'
	textoPSDY = 'Potência'
	textoTituloPSD = r'Power Spectrum Density $\beta$ = '
	
	print("2. Plotting Power Spectrum Density...")

	# Plotagem do PSD    
	PSD = fig.add_subplot(2, 2, 3)    
	PSD.plot(freqs, power, '-', color = corPSD1, alpha = 0.7)
	PSD.plot(xdata, ydata, color = corPSD2, alpha = 0.8)
	PSD.axvline(freqs[INICIO], color = corPSD2, linestyle = '--')
	PSD.axvline(freqs[FIM], color = corPSD2, linestyle = '--')    
	PSD.plot(xdata, powerlaw(xdata, amp, index), 'r-', linewidth = 1.5, label = '$%.4f$' %(b))    
	PSD.set_xlabel(textoPSDX, fontsize = tamanhoFonteEixoX)
	PSD.set_ylabel(textoPSDY, fontsize = tamanhoFonteEixoY)
	PSD.set_title(textoTituloPSD + '%.4f' %(b), loc = 'center', fontsize = tamanhoFonteTitulo)
	PSD.set_yscale('log')
	PSD.set_xscale('log')
	PSD.grid() 
	
	#-----------------------------------------------------------------
	# Cálculo e plotagem do DFA
    #-----------------------------------------------------------------
	        
	# Calcula o DFA 1D
	alfa, vetoutput, x, y, reta, erro = dfa1d(data, 1)

	# Verifica se o DFA possui um valor válido
	# Em caso afirmativo, faz a plotagem
	if not math.isnan(alfa):
		
		# Define as cores da plotagem
		corDFA = 'darkmagenta'

		# Título dos eixos do DFA
		textoDFAX = '$log_{10}$ (s)'
		textoDFAY = '$log_{10}$ F(s)'
		textoTituloDFA = r'Detrended Fluctuation Analysis $\alpha$ = '
		
		print("3. Plotting Detrended Fluctuation Analysis...")
		
		# Plotagem do DFA 
		DFA = fig.add_subplot(2, 2, 4)    
		DFA.plot(x, y, 's', 
				 color = corDFA, 
				 markersize = 4,
				 markeredgecolor = 'r',
				 markerfacecolor = 'None',
				 alpha = 0.8)				 
		DFA.plot(x, reta, '-', color = corDFA, linewidth = 1.5)
		DFA.set_title(textoTituloDFA + '%.4f' %(alfa), loc = 'center', fontsize = tamanhoFonteTitulo)
		DFA.set_xlabel(textoDFAX, fontsize = tamanhoFonteEixoX)
		DFA.set_ylabel(textoDFAY, fontsize = tamanhoFonteEixoY)
		DFA.grid()

	else:  
		DFA = fig.add_subplot(2, 2, 4)
		DFA.set_title(textoTituloDFA + 'N.A.', loc = 'center', fontsize = tamanhoFonteTitulo)
		DFA.grid()

	#-----------------------------------------------------------------
	# Exibe e salva a figura
	#-----------------------------------------------------------------
	plt.suptitle(tituloPrincipal, fontsize = tamanhoFontePrincipal)
	nomeImagem = '3DBMO_PSD_DFA_2.png'
	fig.set_size_inches(15, 9)
	plt.savefig(nomeImagem, dpi = 300, bbox_inches = 'tight', pad_inches = 0.1)	
	plt.show()
