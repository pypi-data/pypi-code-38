# -*- coding: utf-8 -*-
from aiida.orm import DataFactory, CalculationFactory
from aiida.orm.code import Code
from aiida.work.workchain import WorkChain, ToContext, Calc
from aiida.orm.data.upf import get_pseudos_from_structure
from aiida.work.run import submit

UpfData = DataFactory('upf')
ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')

class TestWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super(TestWorkChain, cls).define(spec)
        spec.input("code", valid_type=Code)
        spec.input("structure", valid_type=StructureData)
        spec.outline(
            cls.run_scf,
            cls.run_md,
            cls.return_results,
        )
        spec.dynamic_output()

    def run_scf(self):
        structure = self.inputs.structure
        return self._submit_pw_calc(structure, label="scf", runtype='scf',
                                    wallhours=4)
    
    def run_md(self):
        prev_calc = self.ctx.scf
        structure = self.inputs.structure
        return self._submit_pw_calc(structure, label="md", runtype='md',
                                    wallhours=4, parent_folder=prev_calc.out.remote_folder)

    def _submit_pw_calc(self, structure, label, runtype, wallhours=24, parent_folder=None):
        self.report("Running pw.x for "+label)

        inputs = {}
        inputs['_label'] = label
        inputs['code'] = self.inputs.code
        inputs['structure'] = structure
        inputs['parameters'] = self._get_parameters(structure, runtype, parent_folder)
        inputs['pseudo'] = self._get_pseudos(structure,
                                             family_name="SSSP_efficiency_v1.0")
        if parent_folder:
            inputs['parent_folder'] = parent_folder

        # kpoints
        kpoints = KpointsData()
        kpoints_mesh = 2
        kpoints.set_kpoints_mesh([kpoints_mesh, kpoints_mesh, kpoints_mesh])
        inputs['kpoints'] = kpoints

        inputs['_options'] = {
            "resources": {"num_machines": 1, "num_mpiprocs_per_machine": 1},
            "max_wallclock_seconds": wallhours * 60 * 60,  # hours
        }


        future = submit(PwCalculation.process(), **inputs)
	return ToContext(**{label: Calc(future)})

    def _get_parameters(self, structure, runtype, parent_folder=True):
        params = {'CONTROL': {
                     'calculation': runtype,
                     'wf_collect': True,
                     'forc_conv_thr': 0.0001,
                     'nstep': 4,
                     },
                  'SYSTEM': {
                       'ecutwfc': 50.,
                       'ecutrho': 400.,
                       'occupations': 'smearing',
                       'degauss': 0.001,
                       },
                  'ELECTRONS': {
                       'conv_thr': 1.e-8,
                       'mixing_beta': 0.25,
                       'electron_maxstep': 50,
                       'scf_must_converge': False,
                      },
                  }
        if parent_folder:
            params['CONTROL']['restart_mode'] = 'restart'
        return ParameterData(dict=params)

    def _get_pseudos(self, structure, family_name):
        kind_pseudo_dict = get_pseudos_from_structure(structure, family_name)
        pseudos = {}
        for p in kind_pseudo_dict.values():
            ps = [k for k, v in kind_pseudo_dict.items() if v == p]
            kinds = "_".join(ps)
            pseudos[kinds] = p

        return pseudos

    def return_results(self):
        from aiida.orm.data.base import Int, Float
        i = Int()
        f = Float()
        self.out("integer", i)
        self.out("float", f)

