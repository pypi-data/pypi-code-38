class HTMLgen:
    """
        Basic HTML generator
        02/09/2019

        class HTMLgen(head=False, tail=False, lang="en", docType="html")

        FUNCTIONS:
            title(self, title, scripts=None, css=None)
            body.add(content)
            tag(tag, content=False, close=True, cssclass=None)
            image(src, alt=None, srcset=None, height=None, width=None, style=None, cssclass=None)
            br() <-- Returns a </ br> tag
            div(cssclass) <-- Not yet implemented 
            table() -- Class Object
                table.add_row()
                table.produce_table()

        EXAMPLE:
            page = HTMLgen(True, True)
            page.title("This is the page Title", scripts="foo.js bar.js", css="styles.css nav.css")
            page.body.add(page.image("images/frontpage.jpg", width="100%"))
            page.body.add(page.tag("h1", "This is a header line"))
            page.body.add("This is another line")

            ## Creating a table
            test_table = HTMLgen.table()
            test_table.add_row(["column data 1", "column data 2", "column data 3"])
            test_table.add_row(["column data 4", "column data 5", "column data 6"])

            ## And finally we add the table to the rest of the page
            page.body.add(test_table.produce_table())


            page.return_html()

            ```
                <!DOCTYPE html>
                <html lang="en>
                    <head>
                        <title>This is the page Title</title>
                        <link rel="stylesheet" href="styles.css">
                        <link rel="stylesheet" href="nav.css">
                        <script src="foo.js"></script>
                        <script src="bar.js"></script>
                    </head>
                <body>
                    <img src="images/frontpage.jpg" width="100%">
                    <h1>This is a header line</h1>
                    This is another line
                   	<table>
                        <tr>
                            <td>column data 1</td><td>column data 2</td><td>column data 3</td>
                        </tr>
                        <tr>
                            <td>column data 4</td><td>column data 5</td><td>column data 6</td>
                        </tr>

                    </table>

                </body>
                </html>
            ```

    """

    def __init__(self, head=False, tail=False, lang="en", docType="html"):
        self.head = head
        self.tail = tail
        self.page = {}
        self.body = self.createBody()

        if self.head:
            self.page["head"] = "<!DOCTYPE "+docType+">\n"
            self.page["head"] = self.page["head"]+"<html lang=\""+lang+"\">\n"

        if self.tail:
            self.page["tail"] = '</html>'


    def __exit__(self, exception_type, exception_value, traceback):
        self.return_html(self)


    def title(self, title, scripts=None, css=None):
        output = "\t<head>\n"
        output = output + "\t\t<title>"+title+"</title>\n"
        if css:
            if " " in css:
                css = css.split(' ')
                for i in css:
                    output = output + "\t\t<link rel=\"stylesheet\" href=\""+i+"\">\n"
            else:
                output = output + "\t\t<link rel=\"stylesheet\" href=\""+css+"\">\n"
        if scripts:
            if " " in scripts:
                scripts = scripts.split(' ')
                for script in scripts:
                    output = output + "\t\t<script src=\""+script+"\"></script>\n"
            else:
                output = output + "\t\t<script src=\""+scripts+"\"></script>\n"
            
        output = output + "\t</head>\n"

        self.page["header"] = output


    def tag(self, tag, content=False, close=True, cssclass=None):
        output = "<"+tag
        if cssclass:
            output = output+" class=\""+cssclass+'">'
        else:
            output = output+">"

        if content:
            output = output+content
        if close:
            output = output+"</"+tag+">"

        return output


    def br(self):
        return "</ br>"


    def createBody(self):
        return HTMLgen.bodycontent(self)


    class bodycontent:
        def __init__(self, body):
            self.body = body
            self.content = []

        def add(self, content):
            n = 25
            strings = content.split(' ')
            if len(strings) > n:
                count = 0
                new_content_count = 0
                new_content = []
                content = ""
                for string in strings:
                    if count <= n:
                        count += 1
                    else: 
                        count = 0
                        new_content_count += 1

                    try:
                        new_content[new_content_count] = new_content[new_content_count] + " " + string
                    except IndexError:
                        new_content.append(string)

                for string in new_content:
                    content = content + "\t" + string + "\n"
            
            else:
                content = "\t"+content


            self.content.append(content)


    class table:
        def __init__(self):
            self.rows = []

        def add_row(self, data):
            """
                Row data should be a list of data
            """
            #data = data + "\n"
            self.rows.append(data)

        def produce_table(self):
            table_output = "<table>\n"
            for row in self.rows:
                table_output = table_output+"\t\t<tr>\n\t\t\t"
                for column_data in row:
                    table_output = table_output+"<td>"+column_data+"</td>"
                
                table_output = table_output+"\n"
                table_output = table_output+"\t\t</tr>\n"

            table_output = table_output+"\n\t</table>"

            return table_output

    
    def image(self, src, alt=None, srcset=None, height=None, width=None, style=None, cssclass=None):
        if src:
            image = '<img src="'+src+'"'
        else:
            return False

        if alt:
            image = image + ' alt="'+alt+'"'

        if srcset:
            image = image + ' srcset="'+srcset+'"'

        if height:
            image = image + ' height="'+height+'"'

        if width:
            image = image + ' width="'+width+'"'

        if style:
            image = image + ' style="'+style+'"'

        if cssclass:
            image = image + " class=\""+cssclass+'"'

        image = image + ">"

        return str(image)


    def return_html(self):
        output = ""
        if "head" in self.page:
            output = output + self.page["head"]
        if "header" in self.page:
            output = output + self.page["header"]
        if self.body.content:
            output = output + "<body>\n"
            for i in self.body.content:
                output = output + i + "\n"
            output = output + "</body>\n"
        if "tail" in self.page:
            output = output + self.page["tail"]

        return output