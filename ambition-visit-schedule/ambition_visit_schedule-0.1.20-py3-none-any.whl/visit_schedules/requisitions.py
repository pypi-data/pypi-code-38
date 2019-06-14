from ambition_labs import chemistry_alt_panel, chemistry_panel, csf_chemistry_panel
from ambition_labs import pk_plasma_panel_t12, pk_plasma_panel_t23, pk_plasma_panel_t0
from ambition_labs import pk_plasma_panel_t2, pk_plasma_panel_t4, pk_plasma_panel_t7
from ambition_labs import qpcr_blood_panel, csf_stop_panel, qpcr24_blood_panel
from ambition_labs import serum_panel, plasma_buffycoat_panel, csf_pkpd_panel, wb_panel
from ambition_labs import (
    viral_load_panel,
    cd4_panel,
    fbc_panel,
    csf_panel,
    qpcr_csf_panel,
)
from ambition_sites import ambition_sites
from edc_sites import get_site_id
from edc_visit_schedule import FormsCollection, Requisition


requisitions_prn = FormsCollection(
    Requisition(show_order=10, panel=fbc_panel,
                required=False, additional=False),
    Requisition(show_order=20, panel=chemistry_panel,
                required=False, additional=False),
    Requisition(
        show_order=30, panel=chemistry_alt_panel, required=False, additional=False
    ),
    Requisition(show_order=40, panel=cd4_panel,
                required=False, additional=False),
    Requisition(
        show_order=50, panel=viral_load_panel, required=False, additional=False
    ),
    Requisition(
        show_order=60, panel=csf_chemistry_panel, required=False, additional=False
    ),
    Requisition(show_order=70, panel=csf_panel,
                required=False, additional=False),
    Requisition(
        show_order=80,
        panel=csf_pkpd_panel,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=90,
        panel=pk_plasma_panel_t0,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=100,
        panel=pk_plasma_panel_t2,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=110,
        panel=pk_plasma_panel_t4,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=120,
        panel=pk_plasma_panel_t7,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=130,
        panel=pk_plasma_panel_t12,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=140,
        panel=pk_plasma_panel_t23,
        required=False,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    name="requisitions_prn",
)

requisitions_d1 = FormsCollection(
    Requisition(show_order=10, panel=fbc_panel,
                required=True, additional=False),
    Requisition(
        show_order=20, panel=chemistry_alt_panel, required=True, additional=False
    ),
    Requisition(show_order=30, panel=csf_panel,
                required=True, additional=False),
    Requisition(
        show_order=40, panel=csf_chemistry_panel, required=True, additional=False
    ),
    Requisition(
        show_order=50,
        panel=csf_pkpd_panel,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(show_order=60, panel=qpcr_csf_panel,
                required=True, additional=False),
    Requisition(show_order=70, panel=csf_stop_panel,
                required=False, additional=False),
    Requisition(show_order=80, panel=wb_panel,
                required=True, additional=False),
    Requisition(show_order=90, panel=serum_panel,
                required=True, additional=False),
    Requisition(
        show_order=100, panel=plasma_buffycoat_panel, required=True, additional=False
    ),
    Requisition(
        show_order=120, panel=qpcr_blood_panel, required=True, additional=False
    ),
    Requisition(
        show_order=125, panel=qpcr24_blood_panel, required=True, additional=False
    ),
    Requisition(
        show_order=135,
        panel=pk_plasma_panel_t2,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=145,
        panel=pk_plasma_panel_t4,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=155,
        panel=pk_plasma_panel_t7,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=165,
        panel=pk_plasma_panel_t12,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=175,
        panel=pk_plasma_panel_t23,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    name="requisitions_day1",
)

requisitions_d3 = FormsCollection(
    Requisition(show_order=20, panel=chemistry_panel,
                required=True, additional=False),
    Requisition(
        show_order=40, panel=plasma_buffycoat_panel, required=True, additional=False
    ),
    Requisition(show_order=50, panel=qpcr_blood_panel,
                required=True, additional=False),
    name="requisitions_day3",
)

requisitions_d5 = FormsCollection(
    Requisition(show_order=10, panel=chemistry_panel,
                required=True, additional=False),
    name="requisitions_default",
)

requisitions_d7 = FormsCollection(
    Requisition(show_order=10, panel=fbc_panel,
                required=True, additional=False),
    Requisition(
        show_order=20, panel=chemistry_alt_panel, required=True, additional=False
    ),
    Requisition(show_order=40, panel=csf_panel,
                required=True, additional=False),
    Requisition(
        show_order=50,
        panel=csf_pkpd_panel,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(show_order=60, panel=qpcr_csf_panel,
                required=True, additional=False),
    Requisition(show_order=70, panel=csf_stop_panel,
                required=False, additional=False),
    Requisition(
        show_order=80, panel=plasma_buffycoat_panel, required=True, additional=False
    ),
    Requisition(show_order=90, panel=qpcr_blood_panel,
                required=True, additional=False),
    Requisition(
        show_order=95,
        panel=pk_plasma_panel_t0,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=100,
        panel=pk_plasma_panel_t2,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=110,
        panel=pk_plasma_panel_t4,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=120,
        panel=pk_plasma_panel_t7,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=130,
        panel=pk_plasma_panel_t12,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(
        show_order=140,
        panel=pk_plasma_panel_t23,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    name="requisitions_day7",
)

requisitions_d10 = FormsCollection(
    Requisition(show_order=20, panel=chemistry_panel,
                required=True, additional=False),
    name="requisitions_day10",
)

requisitions_d12 = FormsCollection(
    Requisition(show_order=20, panel=chemistry_panel,
                required=True, additional=False),
    name="requisitions_day12",
)

requisitions_d14 = FormsCollection(
    Requisition(show_order=10, panel=fbc_panel,
                required=True, additional=False),
    Requisition(
        show_order=30, panel=chemistry_alt_panel, required=True, additional=False
    ),
    Requisition(show_order=40, panel=csf_panel,
                required=True, additional=False),
    Requisition(
        show_order=50,
        panel=csf_pkpd_panel,
        required=True,
        additional=False,
        site_ids=[get_site_id("blantyre", sites=ambition_sites)],
    ),
    Requisition(show_order=60, panel=qpcr_csf_panel,
                required=True, additional=False),
    Requisition(show_order=70, panel=csf_stop_panel,
                required=False, additional=False),
    Requisition(
        show_order=80, panel=plasma_buffycoat_panel, required=True, additional=False
    ),
    Requisition(show_order=90, panel=qpcr_blood_panel,
                required=True, additional=False),
    name="requisitions_day14",
)

requisitions_w4 = FormsCollection(
    Requisition(show_order=10, panel=fbc_panel,
                required=True, additional=False),
    Requisition(
        show_order=20, panel=chemistry_alt_panel, required=True, additional=False
    ),
    name="requisitions_week4",
)
