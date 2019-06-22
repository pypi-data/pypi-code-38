# -*- coding: utf-8 -*-

""" this script is created by *AMJoshaghani* for helping web

    developers for using markup and markdown on python script

    :param MD: help you for showing markdown(md) on your script.

    for example:

        Mark2PY.MD.bold('AMJoshaghani')



    :param MU: help you for showing markup(html) on your script.

    for  example:

        Mark2PY.MU.center('AMJoshaghani')



    :copyright : © 2019 by Amir Mohammad Joshaghani --> AMJoshaghani @ https://amjoshaghani.ir

    :license : MIT

"""

import os

import webbrowser

import mistune


########
md_var = ''
mu_var = ''
########
class ModeError(Exception):
    def __str__(self):
    	return repr("Please Enter A Correct Mode. MU or MD")

class Md:

	def H1(text):

    		md_var.join('# {}\n'.format(str(text)))





	def H2(text):

    		md_var.join('## {}\n'.format(str(text)))





	def H3(text):

    		md_var.join('### {}\n'.format(str(text)))





	def bold(text):

    		md_var.join('**{}**\n'.format(str(text)))





	def italic(text):

    		md_var.join('*{}*\n'.format(str(text)))





	def strikethrough(text):

    		md_var.join('~~{}~~\n'.format(str(text)))





	def block_quote(text):

    		md_var.join('> {}\n'.format(str(text)))





	def unordered_list(*arg):

    		for i in arg:

        		md_var.join('- {}\n'.format(str(arg)))





	def ordered_list(*arg):

    		for i in arg:

        		x = 1

        		md_var.join('{}. {}\n'.format(x, str(i)))

        		x += 1





	def horizontal_rule():

    		md_var.join('------------')



	def link(title=str, href=str):

		md_var.join("[{}]({})\n".format(title, str))

	

	#TODO: other statements


class Mu:
	# TODO: MARKUP
	pass


def run(mode):

	if mode == "MD" or "md":
		global md_var
		print(mistune.markdown(md_var))

	elif mode == "MU" or "mu":
		global mu_var
		print(mu_var)		
	else: 
		raise ModeError()

__version__ = '0.5.5.5'
__author__ = 'Amir Mohammad Joshaghani'
__author_email__ = 'amjoshaghani@gmail.com'


def test():
	filename = 'file:///'+os.getcwd()+'/' + 'helloworld.html'
	webbrowser.open_new_tab(filename)

if __name__ == "__main__":
	test()
