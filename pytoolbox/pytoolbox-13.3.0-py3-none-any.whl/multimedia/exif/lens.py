# -*- encoding: utf-8 -*-



from pytoolbox import decorators, module

from . import equipment

_all = module.All(globals())


class Lens(equipment.Equipement):

    @property
    def brand(self):
        brands = set(t.brand for t in self.tags.values() if t.brand)
        if brands:
            assert len(brands) == 1, brands
            return next(iter(brands))

    @property
    def _model(self):
        return next((t.data for t in self.tags.values() if 'model' in t.label.lower()), None)

    @decorators.cached_property
    def tags(self):
        return {k: t for k, t in self.metadata.tags.items() if 'lens' in t.label.lower()}


__all__ = _all.diff(globals())
