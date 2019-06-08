class LuceneParser:
    def __init__(self):
        pass

    def parse(self, lucene):
        # iterate through all fields and values in lucene query
        first = True
        while lucene is not None and lucene != "":
            # find field name, determined by placement of ':'
            colon_index = lucene.find(":")
            field_name = lucene[0:colon_index]

            # trim field name
            lucene = lucene[colon_index+1:].lstrip()

            # parse field value
            whitespace_index = lucene.find(" ")
            if whitespace_index == -1:
                whitespace_index = len(lucene)
            field_value = lucene[0:whitespace_index]

            # trim field value
            lucene = lucene[whitespace_index+1:].lstrip()

            print("field - " + field_name)
            print("value - " + field_value)
            print("sql - " + field_name + " = " + field_value)



parser = LuceneParser

parser.parse("LuceneParser", "name:   mike profession: engineer")
#parser.parse(LuceneParser, "device:'mike'")
#parser.parse(LuceneParser, "-device:'mike'")
#parser.parse(LuceneParser, "gpa:[3.0 TO 4.0]")