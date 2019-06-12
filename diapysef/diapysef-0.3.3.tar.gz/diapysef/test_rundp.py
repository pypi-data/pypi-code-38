import conversions as dp
import pandas as pd
evidence = pd.read_csv("~/Mar2018_helaBenchmark/data/dia/20180911_newLibrary_noDeisotoping/combined_48Fractions_HeLa_120min_200ng_DIA_NoDeisotoping/txt/20180631_TIMS2_annotated/annotated_evidence.csv")
msms = pd.read_csv("~/Mar2018_helaBenchmark/data/dia/20180911_newLibrary_noDeisotoping/combined_48Fractions_HeLa_120min_200ng_DIA_NoDeisotoping/txt/mqout/msms.txt", sep="\t")
pirt = pd.read_csv("~/Mar2018_helaBenchmark/data/irt/pasef_CiRT_all_assaylib.tsv", sep='\t')
#help(dp.pasef_to_tsv)

#pasef_to_tsv(evidence, msms, irt_file=None, pdfout='rtcalibration.pdf', im_column='Ion mobility index', rt_alignment='nonlinear', im_alignment='linear')
#    Converts a mq output to a library taking a best replicate approach.

a = dp.pasef_to_tsv(evidence, msms, irt_file=pirt, im_column="IonMobilityIndexK0")

print(a["iRT"].isnull().sum().sum())

a.to_csv("test_mqout.tsv", sep="\t", index=False)
