"""Jinja2 template collection."""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

BASE_TEMPLATE = ENV.get_template('base_content.html')
LAYOUT_TEMPLATE = ENV.get_template('layout.html')
LAYOUT_RESPONSIVE_TEMPLATE = ENV.get_template('layout_responsive.html')
HEADER_TEMPLATE = ENV.get_template('header.html')
ANCHOR_TEMPLATE = ENV.get_template('anchor.html')
POPOVER_TEMPLATE = ENV.get_template('popover.html')
STATSGRID_TEMPLATE = ENV.get_template('statsgrid.html')
ALERT_TEMPLATE = ENV.get_template('alert.html')
#CARD_TEMPLATE = ENV.get_template('card.html')
CARD_TEMPLATE = ENV.get_template('card.html')
CHART_TEMPLATE = ENV.get_template('chart.html')
COLLAPSIBLE_TEMPLATE = ENV.get_template('collapsible.html')
DETAIL_CARD_TEMPLATE = ENV.get_template('detailcard.html')
IFRAME_TEMPLATE = ENV.get_template('iframe.html')
TABLE_TEMPLATE = ENV.get_template('table.html')
RESPONSIVE_TABLE_TEMPLATE = ENV.get_template('table_mobile_responsive.html')
TABS_TEMPLATE = ENV.get_template('tabs.html')
