class ModelCommonParent():

    @classmethod
    def orderAll(cls,q):
        return q

    @classmethod
    def all(cls,DBSession):
        return cls.orderAll(DBSession.query(cls)).all()
    
    @classmethod
    def byId(cls,id,DBSession):
        return DBSession.query(cls).filter(cls.id==id).first()

    @classmethod
    def byField(cls,field,value,DBSession):
        return DBSession.query(cls).filter(getattr(cls, field)==value).all()
    
    @classmethod
    def byFields(cls,fields,DBSession):
        q = DBSession.query(cls)
        for i,field in enumerate(fields):
            q = q.filter(getattr(cls, field[0])==field[1])
        return q.all()


    @classmethod
    def delete(cls,element,DBSession):
        DBSession.delete(element)
    @classmethod
    def deleteAll(cls,elements,DBSession):
        for e in elements:
            DBSession.delete(e)


    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return unicode(str(self))
