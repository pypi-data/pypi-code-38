from orm_cloud.entity_decorator import entity
from orm_cloud.entity import Entity
from orm_cloud.field_decorator import field


@entity(table_name='things', version=1, primary_key='thing_id', fields=['color', 'size', 'age'])
class Thing(Entity):

    @property
    @field(column_name='thing_id', primary_key=True)
    def thing_id(self):
        return

    @property
    @field(column_name='color')
    def color(self):
        pass

    @property
    @field(column_name='size')
    def size(self):
        pass

    @property
    @field(column_name='age')
    def age(self):
        pass


