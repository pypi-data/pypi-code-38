from browser import html

# ----------------------------------------------------------------------


def material_icon(icon, theme='baseline', **kwargs):
    """"""
    return html.I(Class='{}-{}'.format(theme, icon), **kwargs)


# # ----------------------------------------------------------------------
# def material_icon(icon, theme='baseline', **kwargs):
    # """"""
    # return html.I(Class='{}-{}'.format(theme, icon), **kwargs)


