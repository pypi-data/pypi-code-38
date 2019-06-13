from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import re

from comring.lib import odoo
from comring.tools.finance import do_total_brand

bp = Blueprint('stock_picking', __name__, url_prefix='/stock_picking')

@bp.route('by_brand', methods=['GET', 'POST'])
def by_brand():
    if request.method == 'POST':
        if not g.get('odoo_env', None):
            return redirect(url_for('auth.login'))
        pickings = request.form['pickings']
        if pickings:
            tool = None
            env_kind = g.odoo_env.get('kind', '<UNDEFINED>')
            instance = odoo.get_instance(g.odoo_env_alias)
            instance.connect()
            if env_kind == 'live':
                tool = do_total_brand.DOTotalBrand(instance)
            if env_kind == 'nbm':
                tool = do_total_brand.DOTotalBrandNBM(instance)
            if not tool:
                flash('Environment kind not supported: {}'.format(env_kind), category='danger')
                return render_template('finance/do_report_by_brand.html')

            picking_nums = [s.strip() for s in re.split(r'[^a-zA-Z0-9_#/]+', pickings)]
            tool.do_domain = [['name', 'in', picking_nums]]
            result = tool.main()
            return render_template('finance/do_report_by_brand.html', result=result)

        return redirect(url_for('index'))

    return render_template('finance/do_report_by_brand.html')
