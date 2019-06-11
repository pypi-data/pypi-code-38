import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl

app = QApplication(sys.argv)
webView = QWebEngineView()

# Variant 1: Reasonably fast
webView.load(QUrl('file:////tmp/autosave_The_Holy_City-Timpani_page_001.svg'))

# Variant 2: Slow for small files, not working for big ones
## webView.setHtml('<svg>........')

webView.show()
sys.exit(app.exec_())