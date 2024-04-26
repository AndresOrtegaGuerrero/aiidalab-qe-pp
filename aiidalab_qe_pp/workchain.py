from aiida.plugins import WorkflowFactory
from aiida import orm
PPWorkChain = WorkflowFactory("pp_app.pp")


def get_builder(codes, structure, parameters):


    from copy import deepcopy

    pp_code = codes.pop("pp")


    # Filter the dictionary to include only keys that start with 'calc_'
    calc_parameters = {key: value for key, value in parameters["pp"].items() if key.startswith("calc_")}
    properties_list = [key for key, value in calc_parameters.items() if value]

    #PwCalculation pk
    pwcalc_avail = parameters["pp"]["pwcalc_avail"]
    aiida_node = orm.load_node(pwcalc_avail)

    remote_folder = aiida_node.outputs.remote_folder

    #StructureData Used
    structure = parameters["pp"]["structure"]
    #Parameters
    pp_parameters = {
        "charge_dens": { "spin_component" : parameters["pp"]["charge_dens_options"]} , 
        "ildos": { "emin" : parameters["pp"]["ildos_emin"], "emax" : parameters["pp"]["ildos_emax"]},
        "stm": { "sample_bias" : parameters["pp"]["stm_sample_bias"]},


    }
    properties = orm.List(list=properties_list)
    parameters = orm.Dict(dict=pp_parameters)
    builder = PPWorkChain.get_builder_from_protocol(
        parent_folder=remote_folder,
        pp_code = pp_code,
        parameters=parameters,
        properties=properties,
        structure=structure,
    )


    return builder

workchain_and_builder = {
    "workchain": PPWorkChain,
    "get_builder": get_builder,
}