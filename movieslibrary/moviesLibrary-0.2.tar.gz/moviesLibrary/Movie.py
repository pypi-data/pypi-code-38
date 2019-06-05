class Movie(object):

    title = " "
	year = 0
    fantasy = False
    biography = False
    historical = False

    def __init__(self, title, year, biography, fantasy,  historical):
        self.title = title
        self.year = year
        self.fantasy = fantasy
        self.biography = biography
        self.historical = historical

    def __str__(self):
        return "Title: " + self.title + " year: " + self.year