from plone.dexterity.content import PasteBehaviourMixin


# Patch for plone.dexterity.content.PasteBehaviourMixin._getCopy
def PasteBehaviourMixin_getCopy(self, container):
    # Copy the _v_is_cp and _v_cp_refs flags from the original
    # object (self) to the new copy.
    # This has impact on how children will be handled.
    # When the flags are missing, an Archetypes child object will not have
    # the UID updated in some situations.
    # Copied from Products.Archetypes.Referenceable.Referenceable._getCopy
    is_cp_flag = getattr(self, '_v_is_cp', None)
    cp_refs_flag = getattr(self, '_v_cp_refs', None)
    ob = super(PasteBehaviourMixin, self)._getCopy(container)
    if is_cp_flag:
        setattr(ob, '_v_is_cp', is_cp_flag)
    if cp_refs_flag:
        setattr(ob, '_v_cp_refs', cp_refs_flag)
    return ob
