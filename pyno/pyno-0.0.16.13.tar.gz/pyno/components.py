from pyno import HTML as H

bootstrap_head_before = [
    H.link(rel="stylesheet", href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css", integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4", crossorigin="anonomous"),
    H.script(src='https://code.jquery.com/jquery-3.3.1.slim.min.js', integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo", crossorigin="anonymous")
]

bootstrap_body_after = [
    H.script(src=src, integrity=integrity, crossorigin="anonymous") for src, integrity in (
        ('https://code.jquery.com/jquery-3.3.1.slim.min.js', "sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"),
        ("https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js", "sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ"),
        ("https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js", "sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm"))]

H.defaults['bootstrap_preemble'] = []
H.defaults['bootstrap_postemble'] = []
# Just dump scripts into the defaults and insert them straight into this?
def bootstrap(*content):
    return H.html(
    H.head(*bootstrap_head_before, *H.defaults['bootstrap_preemble']),
    H.body(*content, bootstrap_body_after, *H.defaults['bootstrap_postemble']))


def tabs(tab_definitions):
    return H.div.container_fluid(
                H.div(H.ul.nav.nav_tabs(
                    (H.li.nav_item(
                        H.a.nav_link["active" if n == 0 else ''](name, href=f'#list-chap{n}', data_toggle='tab')) for n, name in enumerate(tab_definitions.keys()))), role='Navigation'),
                H.div.tab_content(
                    (H.div.tab_pane.fade.show["active" if n == 0 else ''](content, id=f"list-chap{n}") for n, content in enumerate(tab_definitions.values()))))



style = H.style("""body { padding-top: 5rem; }
main>div {padding: 3rem 1.5rem;text-align: center;}""")

H.defaults['bootstrap_preemble'] += [style]

H.defaults['nav'] = dict(Class='navbar navbar-expand-md navbar-dark bg-dark fixed-top')

def default_navbar(*args, **kwargs):
    return H.nav(
        H.a.navbar_brand('Navbar', href='#'),
        H.button.navbar_toggler(H.span(Class='navbar-toggler-icon'), type='button', data_toggle='collapse', data_target='#navbarsExampleDefault', aria_controls="navbarsExampleDefault", aria_expanded='false', aria_label='Toggle navigation"'),
        H.div.collapse.navbar_collapse(
            H.ul.navbar_nav.mr_auto(
                H.li.nav_item['active'](H.a.nav_link('Home', H.span.sr_only('(current)'))),
                H.li.nav_item(H.a.nav_link('Link')),
                # H.li.nav_item(H.a.nav_link['disabled']('Disabled')),
                H.li.nav_item.dropdown(
                H.a.nav_link.dropdown_toggle('Dropdown'),
                H.div.dropdown_menu(
                map(H.a.dropdown_item, ('Action', 'Action 2')),
                ),
                    href="https://example.com", Id="dropdown01", data_toggle="dropdown", aria_haspopup="true", aria_expanded="false"),
            ),
            H.form.form_inline['my-2 my-lg-0'](
                H.input.form_control['mr-sm-2'](type='text', placeholder='Search', aria_label='Search'),
                H.button.btn['btn-outline-success my-2 my-sm-0']('Search', type='submit')
            ), id="navbarsExampleDefault"),
        )
