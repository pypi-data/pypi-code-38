from markyp_highlightjs import *

def test_HighlightJSCDN():
    assert CDN.CDN_URL == "https://cdnjs.cloudflare.com/ajax/libs/highlight.js"
    assert CDN.VERSION == "9.15.6"
    assert CDN.cdn_url_with_version() ==\
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6"
    assert CDN.url_for_js() ==\
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"
    assert CDN.url_for_style("default") ==\
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/default.min.css"

def test_js():
    assert js.js_import.markup ==\
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"></script>'

    assert js.js_init.markup ==\
        '<script >\nhljs.initHighlightingOnLoad();\n</script>'

    js_import, js_init = js.js
    assert str(js_import) ==\
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"></script>'
    assert str(js_init) ==\
        '<script >\nhljs.initHighlightingOnLoad();\n</script>'

def test_themes():
    assert str(themes.atom_one_dark) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/atom-one-dark.min.css">'
    assert str(themes.atom_one_light) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/atom-one-light.min.css">'
    assert str(themes.darcula) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/darcula.min.css">'
    assert str(themes.default) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/default.min.css">'
    assert str(themes.github) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/github.min.css">'
    assert str(themes.github_gist) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/github-gist.min.css">'
    assert str(themes.idea) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/idea.min.css">'
    assert str(themes.monokai) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/monokai.min.css">'
    assert str(themes.solarized_dark) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/solarized-dark.min.css">'
    assert str(themes.solarized_light) ==\
        '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/solarized-light.min.css">'

def test_highlight():
    assert highlight("import antigravity", language="python").markup ==\
        '<pre >\n<code class="python">import antigravity</code>\n</pre>'

    assert highlight("import antigravity", language="python", class_="my-pre").markup ==\
        '<pre class="my-pre">\n<code class="python">import antigravity</code>\n</pre>'

    assert highlight("import antigravity", language="python", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="python">import antigravity</code>\n</pre>'

def test_bash():
    assert bash("whatever code").markup ==\
        '<pre >\n<code class="bash">whatever code</code>\n</pre>'
    assert bash("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="bash">whatever code</code>\n</pre>'

def test_css():
    assert css("whatever code").markup ==\
        '<pre >\n<code class="css">whatever code</code>\n</pre>'
    assert css("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="css">whatever code</code>\n</pre>'

def test_html():
    assert html("whatever code").markup ==\
        '<pre >\n<code class="html">whatever code</code>\n</pre>'
    assert html("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="html">whatever code</code>\n</pre>'

def test_javascript():
    assert javascript("whatever code").markup ==\
        '<pre >\n<code class="javascript">whatever code</code>\n</pre>'
    assert javascript("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="javascript">whatever code</code>\n</pre>'

def test_json():
    assert json("whatever code").markup ==\
        '<pre >\n<code class="json">whatever code</code>\n</pre>'
    assert json("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="json">whatever code</code>\n</pre>'

def test_markdown():
    assert markdown("whatever code").markup ==\
        '<pre >\n<code class="markdown">whatever code</code>\n</pre>'
    assert markdown("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="markdown">whatever code</code>\n</pre>'

def test_python():
    assert python("whatever code").markup ==\
        '<pre >\n<code class="python">whatever code</code>\n</pre>'
    assert python("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="python">whatever code</code>\n</pre>'

def test_sql():
    assert sql("whatever code").markup ==\
        '<pre >\n<code class="sql">whatever code</code>\n</pre>'
    assert sql("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="sql">whatever code</code>\n</pre>'

def test_xml():
    assert xml("whatever code").markup ==\
        '<pre >\n<code class="xml">whatever code</code>\n</pre>'
    assert xml("whatever code", class_="my-pre", attr=42).markup ==\
        '<pre attr="42" class="my-pre">\n<code class="xml">whatever code</code>\n</pre>'
