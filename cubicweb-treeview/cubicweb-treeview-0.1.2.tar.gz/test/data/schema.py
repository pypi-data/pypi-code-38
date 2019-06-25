from yams.buildobjs import (EntityType, SubjectRelation, String)


class Note(EntityType):
    content = String()
    has_note = SubjectRelation('Note')
