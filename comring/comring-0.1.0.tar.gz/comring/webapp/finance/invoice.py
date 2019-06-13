from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import re

from comring.lib import odoo
from comring.tools.finance import inv_total_brand

bp = Blueprint('invoice', __name__, url_prefix='/invoice')

@bp.route('by_brand', methods=['GET', 'POST'])
def by_brand():
    if request.method == 'POST':
        if not g.get('odoo_env', None):
            return redirect(url_for('auth.login'))
        invoices = request.form['invoices']
        if invoices:
            itb = None
            env_kind = g.odoo_env.get('kind', '<UNDEFINED>')
            instance = odoo.get_instance(g.odoo_env_alias)
            instance.connect()
            if env_kind == 'live':
                itb = inv_total_brand.InvTotalBrand(instance)
            if env_kind == 'nbm':
                itb = inv_total_brand.InvTotalBrandNBM(instance)
            if not itb:
                flash('Environment kind not supported: {}'.format(env_kind), category='danger')
                return render_template('finance/invoice_report_by_brand.html')

            inv_num_list = [s.strip() for s in re.split(r'[^a-zA-Z0-9_#/]+', invoices)]
            itb.inv_domain = [['number', 'in', inv_num_list]]
            result = itb.main()
            return render_template('finance/invoice_report_by_brand.html', result=result)

        return redirect(url_for('index'))

    return render_template('finance/invoice_report_by_brand.html')
