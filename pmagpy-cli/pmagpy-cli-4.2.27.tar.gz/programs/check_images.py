#!/usr/bin/env pythonw

from pmagpy import contribution_builder as cb
import os
import glob
os.system('new_make_magic_plots.py 2> all_errors.out')
image_df = cb.MagicDataFrame("images.txt")
# what is actually in the directory
png_list = glob.glob("*_.png")
# what is in the images file
png_recs = image_df.df[image_df.df.file.str.endswith(".png")]
# these ones are missing from the images file, but are created by new_make_magic_plots.py
print([png for png in png_list if png not in png_recs.file.values])
