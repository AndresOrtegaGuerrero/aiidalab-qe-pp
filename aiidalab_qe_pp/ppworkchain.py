from aiida.plugins import CalculationFactory
from aiida.engine import ToContext, WorkChain, if_
from aiida_quantumespresso.utils.mapping import prepare_process_inputs
from aiida import orm
from aiida.common import AttributeDict



PpCalculation = CalculationFactory("quantumespresso.pp")

def get_parameters(calc_type: str, settings: dict) -> orm.Dict:
    """Return the parameters based on the calculation type, with optional settings."""

    # Existing code with slight modifications for safe accessing
    calc_config = {
        "charge_dens": {
            "plot_num": 0,
            "extra_params": {
                "spin_component": settings.get("spin_component", 1),
            }
        },
        "spin_dens": {
            "plot_num": 6,
            "extra_params": {}
        },
        "wfn": {
            "plot_num": 7,
            "extra_params": {
                "kpoint(1)": settings.get("kpoint(1)", 0),  # Default values or handle appropriately
                "kpoint(2)": settings.get("kpoint(2)", 0),
                "kband(1)": settings.get("kband(1)", 0),
                "kband(2)": settings.get("kband(2)", 0)
            }
        },
        "stm": {
            "plot_num": 5,
            "extra_params": {
                "sample_bias": settings.get("sample_bias", 0.0)  # Default value
            }
        },
        "ildos": {
            "plot_num": 10,
            "extra_params": {
                "emin": settings.get("emin", -10),  # Reasonable default
                "emax": settings.get("emax", 10),
                "spin_component": settings.get("spin_component", 1)
            }
        }
    }

    config = calc_config.get(calc_type, {})
    parameters = {
        "INPUTPP": {
            "plot_num": config.get("plot_num"),
            **config.get("extra_params", {})
        },
        "PLOT": {
            "iflag": 3,
        }
    }
    
    return orm.Dict(parameters)


class PPWorkChain(WorkChain):
    "WorkChain to compute vibrational property of a crystal."
    label = "pp"

    @classmethod
    def define(cls, spec):
        """Define the process specification."""
        super().define(spec)
        spec.input('structure', valid_type=orm.StructureData, required=False,)
        spec.input('parent_folder', valid_type=(orm.RemoteData, orm.FolderData), required=True,
            help='Output folder of a completed `PwCalculation`')
        spec.input('properties', valid_type=orm.List, default=lambda: orm.List(),
                   help='The properties to calculate, used to control the logic of PPWorkChain.')
        spec.input('parameters', valid_type=orm.Dict, required=False,)
        spec.expose_inputs(PpCalculation, namespace='pp_calc', exclude=['parent_folder','parameters'])
        spec.outline(
            if_(cls.should_run_charge_dens)(
                cls.run_charge_dens,
                cls.inspect_charge_dens,
            ),
            if_(cls.should_run_spin_dens)(
                cls.run_spin_dens,
                cls.inspect_spin_dens,
            ),
            if_(cls.should_run_wfn)(
                cls.run_wfn,
                cls.inspect_wfn,
            ),
            if_(cls.should_run_ildos)(
                cls.run_ildos,
                cls.inspect_ildos,
            ),
            if_(cls.should_run_stm)(
                cls.run_stm,
                cls.inspect_stm,
            ),
            cls.results,
        )
        
        spec.expose_outputs(
            PpCalculation, namespace='charge_dens',
            namespace_options={'required': False, 'help': 'Charge Density `PpCalculation`.'},
        )
        spec.expose_outputs(
            PpCalculation, namespace='spin_dens',
            namespace_options={'required': False, 'help': 'Spin Density `PpCalculation`.'},
        )
        spec.expose_outputs(
            PpCalculation, namespace='wfn',
            namespace_options={'required': False, 'help': 'Wavefunction `PpCalculation`.'},
        )
        spec.expose_outputs(
            PpCalculation, namespace='ildos',
            namespace_options={'required': False, 'help': 'ILDOS `PpCalculation`.'},
        )
        spec.expose_outputs(
            PpCalculation, namespace='stm',
            namespace_options={'required': False, 'help': 'STM `PpCalculation`.'},
        )

        spec.exit_code(201, 'ERROR_CHARGE_DENS_FAILED', message='The charge density calculation failed.')
        spec.exit_code(202, 'ERROR_SPIN_DENS_FAILED', message='The spin density calculation failed.')
        spec.exit_code(203, 'ERROR_WFN_FAILED', message='The wavefunction calculation failed.')
        spec.exit_code(204, 'ERROR_ILDOS_FAILED', message='The ILDOS calculation failed.')
        spec.exit_code(205, 'ERROR_STM_FAILED', message='The STM calculation failed.')
        spec.exit_code(206, 'ERROR_SUB_PROCESS_FAILED', message='One (or more) of the sub processes failed.')


    @classmethod
    def get_builder_from_protocol(
        cls,
        parent_folder, 
        pp_code,
        parameters,
        properties,
        protocol=None,
        options=None,
        structure=None, #To remove once we update to new version!
        **kwargs,
        ):

        

        #if options:
        #    metadata['options'] = recursive_merge(inputs['pw']['metadata']['options'], options)

        """Return a builder pre-set with the protocol values."""
        builder = cls.get_builder()

        builder.parent_folder = parent_folder
        builder.properties = properties
        builder.pp_calc.code = pp_code

        #Temporary while we update to the new resources schema
        builder.pp_calc.metadata.options.resources = {
                "num_machines": 1,
                "num_mpiprocs_per_machine": 1,
            } 
        builder.parameters = parameters
        builder.structure = structure

        

        
        return builder


    def should_run_charge_dens(self):
        return "calc_charge_dens" in self.inputs.properties

    def run_charge_dens(self):
        inputs = AttributeDict(self.exposed_inputs(PpCalculation, namespace="pp_calc"))
        inputs.parent_folder = self.inputs.parent_folder
        charge_dens_parameters = get_parameters("charge_dens", self.inputs.parameters["charge_dens"]) 
        inputs.parameters = charge_dens_parameters
        running = self.submit(PpCalculation, **inputs)
        self.report(f"launching Charge Density PpCalculation<{running.pk}>")
        return ToContext(calc_charge_dens=running)

    def inspect_charge_dens(self):
        """Inspect the results of the charge density calculation."""
        calculation = self.ctx.calc_charge_dens

        if not calculation.is_finished_ok:
            self.report(f"Charge Density PpCalculation failed with exit status {calculation.exit_status}")
            return self.exit_codes.ERROR_CHARGE_DENS_FAILED


    def should_run_spin_dens(self):
        return "calc_spin_dens" in self.inputs.properties

    def run_spin_dens(self):
        inputs = AttributeDict(self.exposed_inputs(PpCalculation, namespace="pp_calc"))
        inputs.parent_folder = self.inputs.parent_folder
        spin_dens_parameters = get_parameters("spin_dens", {}) 
        inputs.parameters = spin_dens_parameters
        running = self.submit(PpCalculation, **inputs)
        self.report(f"launching Spin Density PpCalculation<{running.pk}>")
        return ToContext(calc_spin_dens=running)

    def inspect_spin_dens(self):
        """ Inspect the results of the spin density calculation."""
        calculation = self.ctx.calc_spin_dens

        if not calculation.is_finished_ok:
            self.report(f"Spin Density PpCalculation failed with exit status {calculation.exit_status}")
            return self.exit_codes.ERROR_SPIN_DENS_FAILED

    def should_run_wfn(self):
        return "calc_wfn" in self.inputs.properties
    
    def run_wfn(self):
        inputs = AttributeDict(self.exposed_inputs(PpCalculation, namespace="pp_calc"))
        inputs.parent_folder = self.inputs.parent_folder
        wfn_parameters = get_parameters_wfn(self.inputs.parameters["wfn"])
        inputs.parameters = wfn_parameters
        running = self.submit(PpCalculation, **inputs)
        self.report(f"launching Wavefunction PpCalculation<{running.pk}>")
        return ToContext(calc_wfn=running)

    def inspect_wfn(self):
        pass

    def should_run_ildos(self):
        return "calc_ildos" in self.inputs.properties
    
    def run_ildos(self):
        inputs = AttributeDict(self.exposed_inputs(PpCalculation, namespace="pp_calc"))
        inputs.parent_folder = self.inputs.parent_folder
        ildos_parameters = get_parameters("ildos", self.inputs.parameters["ildos"])
        inputs.parameters = ildos_parameters
        running = self.submit(PpCalculation, **inputs)
        self.report(f"launching ILDOS PpCalculation<{running.pk}>")
        return ToContext(calc_ildos=running)
    
    def inspect_ildos(self):
        """Inspect the results of the ILDOS calculation."""
        calculation = self.ctx.calc_ildos

        if not calculation.is_finished_ok:
            self.report(f"ILDOS PpCalculation failed with exit status {calculation.exit_status}")
            return self.exit_codes.ERROR_ILDOS_FAILED

    def should_run_stm(self):
        return "calc_stm" in self.inputs.properties

    def run_stm(self):
        inputs = AttributeDict(self.exposed_inputs(PpCalculation, namespace="pp_calc"))
        inputs.parent_folder = self.inputs.parent_folder
        stm_parameters = get_parameters("stm", self.inputs.parameters["stm"])
        inputs.parameters = stm_parameters
        running = self.submit(PpCalculation, **inputs)
        self.report(f"launching STM PpCalculation<{running.pk}>")
        return ToContext(calc_stm=running)

    def inspect_stm(self):
        """Inspect the results of the STM calculation."""
        calculation = self.ctx.calc_stm

        if not calculation.is_finished_ok:
            self.report(f"STM PpCalculation failed with exit status {calculation.exit_status}")
            return self.exit_codes.ERROR_STM_FAILED

    def results(self):
        """Attach the results of the PPWorkChain to the outputs."""
        failed = False
        for prop in self.inputs.properties:
            if  self.ctx[f'{prop}'].is_finished_ok:
                if prop == "calc_charge_dens":
                    self.out_many(
                        self.exposed_outputs(
                            self.ctx.calc_charge_dens, PpCalculation, namespace="charge_dens"
                        )
                    )
                elif prop == "calc_spin_dens":
                    self.out_many(
                        self.exposed_outputs(
                            self.ctx.calc_spin_dens, PpCalculation, namespace="spin_dens"
                        )
                    )
                elif prop == "calc_wfn":
                    self.out("wfn", self.ctx.calc_wfn.outputs.output_data)
                elif prop == "calc_ildos":
                    self.out_many(
                        self.exposed_outputs(
                            self.ctx.calc_ildos, PpCalculation, namespace="ildos"
                        )
                    )
                elif prop == "calc_stm":
                    self.out_many(
                        self.exposed_outputs(
                            self.ctx.calc_stm, PpCalculation, namespace="stm"
                        )
                    )
            else:
                self.report(f"{prop} calculation failed")
                failed = True
        if failed:
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED
        else:
            self.report("PPWorkChain completed successfully")




    