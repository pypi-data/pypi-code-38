
import textwrap



string = '''     
Explanation for why sum(publcount) is lower 
than expected for name=Ax,venue=ICDE,year=2009:
Even though like many other authors, year predicts 
sum(pubcount) for author = Ax (left graph), Ax's publication
in venue=icde, year=2009 is low which maybe explained by his higher than usual
number of publications in year = 2008, venue = icde(right graph)
    	'''

lists = textwrap.wrap(string)

formatted_string = '\n'.join(lists)

print(formatted_string)

