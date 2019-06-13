# -*- coding: utf-8 -*-
from wordweaver.app import app
from flask import render_template, url_for
import os
from logging import getLogger

logger = getLogger('root')

@app.route('/')
def home():    
    logger.debug("Template rendered successfully")
    return render_template('web.html')

@app.route('/docs')
def swag():
    return render_template('swag.html')
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('web.html'), 404
