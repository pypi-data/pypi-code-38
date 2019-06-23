from .relationship import INNER, OUTER
from .lib import get_service_database


class RelationshipManager(object):
    objects_field = ''

    def __init__(self, source, key, definition, target_class):
        self.source = source
        self.source_class = source.__class__
        self.name = key
        self.definition = definition
        self.target_class = target_class

        if self.definition['strategy'] == INNER:
            self._db = get_service_database()

    def all(self):
        return_set = []
        objects = getattr(self.target_class, self.objects_field)

        if self.definition['strategy'] == INNER:
            fld = getattr(self.source, self.definition['field_name'])
            return_set = objects.filter(pk__in=fld)
        elif self.definition['definition'] == OUTER:
            p_label, c_label = self.source_class.__name__, self.target_class.__name__

            query = f"""
            MATCH (parent:{p_label})-[HAS]->(child:{c_label})
            WHERE parent.uid={self.source.uid}
            RETURN DISTINCT collect(child.uid)
            """
            result = self._db.cypher_query(query)
            return_set = objects.filter(uid__in=result[0][0])
        return return_set

    def connect(self, target_instance):
        if self.definition['strategy'] == INNER:
            setattr(self.source,
                    self.definition['field_name'],
                    target_instance.uid)
            return True
        elif self.definition['definition'] == OUTER:
            p_label, c_label = self.source_class.__name__, self.target_class.__name__

            query = f"""
            MATCH (child:{p_label}) WHERE c.uid={target_instance.uid}
            MATCH (parent:{c_label}) WHERE p.uid={self.source.uid}
            MERGE (parent)-[:HAS]->(child)
            """
            self._db.cypher_query(query)
            return True

        return False

    def delete(self, target_instance):
        if self.definition['strategy'] == INNER:
            fld = getattr(self.source, self.definition['field_name'])
            fld.remove(target_instance.uid)
            return True
        elif self.definition['definition'] == OUTER:
            p_label, c_label = self.source_class.__name__, self.target_class.__name__

            query = f"""
            MATCH (child:{p_label}) WHERE c.uid={target_instance.uid}
            MATCH (parent:{c_label}) WHERE p.uid={self.source.uid}
            MATCH (parent)-[rel:HAS]->(child)
            DELETE rel
            """
            self._db.cypher_query(query)
            return True

        return False


class RelationalManager(RelationshipManager):
    objects_field = 'objects'


class GraphManager(RelationshipManager):
    objects_field = 'nodes'


class DocumentManager(RelationshipManager):
    objects_field = 'objects'
