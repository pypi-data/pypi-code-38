from api.datab import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(80),primary_key=True, default='234')
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)