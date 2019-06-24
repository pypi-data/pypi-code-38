        calculated_layers = None
        try:
            from sage.combinat.posets.posets import Poset, FinitePoset
            p = Poset(self.obj)
            if issubclass(type(p), FinitePoset):
                print("OK")
                # Here, we can compute some sensible default layers
                calculated_layers = {}
                level_sets = p.level_sets() 
                for l in level_sets:
                    for n in l:
                        calculated_layers[n] = int(level_sets.index(l))
        except:
            pass

###

            if calculated_layers: # for posets
                options['layer'] = calculated_layers[n]
