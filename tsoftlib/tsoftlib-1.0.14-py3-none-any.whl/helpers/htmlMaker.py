import datetime
from .fileMaker import makeFolderIfNotExists

DEFAULTOUTPUTPATH = './output'


def makeRow(color, column, value):
    return f"""<tr style="box-sizing: border-box; outline: 0px;"><td class="text-right" style="box-sizing: border-box; outline: 0px; padding: 8px; border-top: 1px solid rgb(221, 221, 221); border-right-color: rgb(229, 229, 229) !important; border-bottom: 1px solid rgb(229, 229, 229); border-left: 0px; text-align: right; vertical-align: top; line-height: 1.6875; width: 326px;"><span class="color" style="box-sizing: border-box; outline: 0px; color: {color};">{column}</span></td><td style="box-sizing: border-box; outline: 0px; padding: 8px; border-top: 1px solid rgb(221, 221, 221); border-right-color: rgb(229, 229, 229) !important; border-bottom: 1px solid rgb(229, 229, 229); border-left: 1px solid rgb(229, 229, 229); vertical-align: top; line-height: 1.6875;">{value}</td>"""

# both list


def makeHTMLTable(columns, values):
    html = ""

    head = f"""<div><table class="table table-params" style="box-sizing: border-box; outline: 0px; border-spacing: 0px; border-collapse: collapse; background-color: transparent; margin-bottom: 27px; width: 1088px; max-width: 100%; color: rgb(119, 119, 119); font-family: 'open sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 14px;"><tbody style="box-sizing: border-box; outline: 0px;">"""

    end = """</tr></tbody></table></div> <style>@media only screen and (max-width:760px),(min-device-width:768px) and (max-device-width:1024px){tbody,td,tr{width:100vw;display:flex;padding:0;margin:0}tbody{flex-direction:column;flex-wrap:wrap}tr{flex-direction:column;border-left:.5px solid #e5e5e5;border-right:.5px solid #e5e5e5;border-right-color:#e5e5e5;border-left-color:#e5e5e5}td{border-bottom:none;border-top:none}}span{ min-width: 0 !important}</style>"""

    html += head
    for i in range(len(columns)):
        html += makeRow('rgb(180, 150, 11)', columns[i], values[i])

    html += end

    return html


def writeToFile(html):
    makeFolderIfNotExists(DEFAULTOUTPUTPATH)
    now = datetime.datetime.now()
    s = now.strftime('%d-%m-%y:%H:%M:%S:%s')
    with open(f'{DEFAULTOUTPUTPATH}/{s}.html', 'w') as file:
        file.write(html)
        file.close()

# col => list | values list of dict


def makeMailHTML(columns, values):
    html = "<table style=\"width: 100%\"><thead><tr>"

    for c in columns:
        html += f"<th style=\"background-color: #069;color: #fff;height: 20px;text-align: left;border: .5px solid #000;\">{c}</th>"
    html += "</tr></thead><tbody>"

    for v in values:
        html += "<tr>"
        for d in v.values():
            html += f"<td style=\"color: #000;vertical-align: bottom;height: 20px;text-align: left;border: .5px solid #000;\">{d}</td>"
        html += "</tr>"
    
    html += "</tbody></table>\n"
    
    return html

