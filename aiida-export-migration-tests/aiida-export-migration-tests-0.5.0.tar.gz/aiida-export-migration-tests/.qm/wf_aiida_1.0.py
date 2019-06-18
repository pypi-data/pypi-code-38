# -*- coding: utf-8 -*-
from aiida.plugins.factories import DataFactory, CalculationFactory
from aiida.orm import Code
from aiida.orm import Int, Float, Str
from aiida.engine import WorkChain, ToContext
from aiida.orm.nodes.data.upf import get_pseudos_from_structure
from aiida_quantumespresso.utils.pseudopotential import validate_and_prepare_pseudos_inputs
from aiida_quantumespresso.utils.mapping import prepare_process_inputs

UpfData = DataFactory('upf')
Dict = DataFactory('dict')
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
        spec.output("integer", valid_type=Int)
        spec.output("float", valid_type=Float)

    def run_scf(self):
        structure = self.inputs.structure
        return self._submit_pw_calc(structure, label="scf", runtype='scf',
                                    wallhours=4)
    
    def run_md(self):
        prev_calc = self.ctx.scf
        structure = self.inputs.structure
        return self._submit_pw_calc(structure, label="md", runtype='md',
                                    wallhours=4, parent_folder=prev_calc.outputs.remote_folder)

    def _submit_pw_calc(self, structure, label, runtype, wallhours=24, parent_folder=None):
        self.report("Running pw.x for "+label)

        inputs = {}
        inputs['_label'] = label
        inputs['code'] = self.inputs.code
        inputs['structure'] = structure
        inputs['parameters'] = self._get_parameters(structure, runtype, parent_folder)
        inputs['settings'] = Dict(dict={}).store()
        p = Str("SSSP_efficiency_v1.0")
        inputs['pseudos'] = validate_and_prepare_pseudos_inputs(structure, None, p)
        if parent_folder:
            inputs['parent_folder'] = parent_folder

        # kpoints
        kpoints = KpointsData()
        kpoints_mesh = 2
        kpoints.set_kpoints_mesh([kpoints_mesh, kpoints_mesh, kpoints_mesh])
        inputs['kpoints'] = kpoints
        options = {
                "resources": {
                    "num_machines": 1,
                    "num_mpiprocs_per_machine": 1,
                    },
                "max_wallclock_seconds": wallhours * 60 * 60,  # hours
                }
        inputs['metadata'] = {'options': options}


        inputs = prepare_process_inputs(PwCalculation, inputs)
        running = self.submit(PwCalculation, **inputs)
        return ToContext(**{label:running})

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
        return Dict(dict=params)

    def return_results(self):
        i = Int()
        f = Float()
        self.out("integer", i)
        self.out("float", f)

