import time
import webbrowser
import tempfile

HTML = """
<html>
<body>
<div style="margin: 24px auto 12px; max-width: 1055px;">
<h1>{0}</h1>
<p>Published at: {1}</p>
<center><img src="{2}" width="400px" /></center>
<p>{3}</p>
See at <a href="{4}">original URL</a>
</div>
<iframe src="{4}" style="width: 100%; height: 600px"></iframe>
</body>
</html>
"""


def article(title, date, image, body, url):
    return HTML.format(title, date, image, body, url)


def view_html(x):
    with tempfile.NamedTemporaryFile(mode="w", suffix='.html', delete=False) as f:
        f.write(x)
        f.flush()
        webbrowser.open('file://' + f.name)
        time.sleep(1)
