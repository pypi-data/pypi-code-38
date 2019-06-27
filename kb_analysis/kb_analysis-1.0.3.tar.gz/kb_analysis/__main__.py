"""Command Line programs for analyzing data

:Author: Gabrielle Altman <gabrielle.altman@wustl>
:Author: Yin Hoon Chew <yinhoon.chew@mssm.edu>
:Date: 2019-06-17
:Copyright: 2019, Karr Lab
:License: MIT
"""
import core 
import core2 as core2
import utils as utils
import matplotlib.pyplot as plt
import time


##start_time = time.time()
##file = core.ProtTranAbundance('/Users/gabriellealtman/Documents/lab/h1_hesc/h1_hesc/kb_gen/core.xlsx')
##
##print(time.time()-start_time)
##prot, tran = file.extract()
##
##print(time.time()-start_time)
##coeff , pval = utils.calculatePearsons(prot, tran)
##print(coeff)
##print(pval)
##
##coeff , pval = utils.calculateSpearmans(prot, tran)
##print(coeff)
##print(pval)
##
##coeff , pval = utils.calculateKendalls(prot, tran)
##print(coeff)
##print(pval)
##
##
##print(utils.calculateDistance(prot,tran))
##print(time.time()-start_time)
##
##plt.scatter(prot.Value, tran.Value)
##plt.xlabel('Protein Abundance')
##plt.ylabel('Transcript Abundance')
##plt.show()

open = core2.openKB()
kb = open.runKB()

length = core2.lengths(kb)
prot, tran, gene = length.extractLengths()

print('prot/tran')
coeff , pval = utils.calculatePearsons(prot, tran)
print(coeff)
print(pval)

coeff , pval = utils.calculateSpearmans(prot, tran)
print(coeff)
print(pval)

coeff , pval = utils.calculateKendalls(prot, tran)
print(coeff)
print(pval)


print(utils.calculateDistance(prot,tran))

print('prot/gene')

coeff , pval = utils.calculatePearsons(prot, gene)
print(coeff)
print(pval)

coeff , pval = utils.calculateSpearmans(prot, gene)
print(coeff)
print(pval)

coeff , pval = utils.calculateKendalls(prot, gene)
print(coeff)
print(pval)


print(utils.calculateDistance(prot,gene))

print('tran/gene')

coeff , pval = utils.calculatePearsons(tran, gene)
print(coeff)
print(pval)

coeff , pval = utils.calculateSpearmans(tran, gene)
print(coeff)
print(pval)

coeff , pval = utils.calculateKendalls(tran, gene)
print(coeff)
print(pval)


print(utils.calculateDistance(gene,tran))


plt.scatter(prot.Value,tran.Value)
plt.savefig('foo.png')

plt.show()


