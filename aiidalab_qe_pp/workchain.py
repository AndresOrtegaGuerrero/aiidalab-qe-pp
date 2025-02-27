from aiida.plugins import WorkflowFactory
from aiida import orm
from aiidalab_widgets_base.utils import string_range_to_list
from aiidalab_qe.utils import set_component_resources


PPWorkChain = WorkflowFactory("pp_app.pp")


def condense_integer_list(lst):
    ranges = []
    current_range = []

    for i, num in enumerate(lst):
        if i == 0:
            current_range.append(num)
        elif num == lst[i - 1] + 1:
            current_range.append(num)
        else:
            if len(current_range) == 1:
                ranges.append(current_range[0])
            else:
                ranges.append([current_range[0], current_range[-1]])
            current_range = [num]

    if current_range:
        if len(current_range) == 1:
            ranges.append(current_range[0])
        else:
            ranges.append([current_range[0], current_range[-1]])

    return ranges


def parse_list_of_tuples(input_list, lsda, number_of_k_points):
    result_list = []

    for item in input_list:
        # Convert string ranges to list of integers
        bands, valid = string_range_to_list(item[0], shift=0)

        # If conversion was successful, add bands to k_point_info
        if valid:
            orbital_list = condense_integer_list(bands)
            for orbital in orbital_list:
                k_point_info = {
                    "kpoint": item[1]
                }  # Create a new dictionary for each orbital
                if isinstance(orbital, int):
                    k_point_info["kband(1)"] = orbital
                else:
                    imin = min(orbital)
                    imax = max(orbital)
                    k_point_info["kband(1)"] = imin
                    k_point_info["kband(2)"] = imax
                result_list.append(k_point_info)

    if lsda:
        temp_list = []
        for entry in result_list:
            temp_entry = (
                entry.copy()
            )  # Create a copy to avoid modifying the original data
            temp_entry["kpoint"] += number_of_k_points
            temp_list.append(temp_entry)
        result_list.extend(temp_list)

    return result_list


def update_resources(builder, codes):
    set_component_resources(builder.pp_calc, codes.get("pp"))


def get_builder(codes, structure, parameters):
    pp_code = codes.get("pp")["code"]
    critic2_code = codes.get("critic2")["code"]
    python_code = codes.get("python")["code"]
    # Filter the dictionary to include only keys that start with 'calc_'
    calc_parameters = {
        key: value for key, value in parameters["pp"].items() if key.startswith("calc_")
    }
    properties_list = [key for key, value in calc_parameters.items() if value]

    # PwCalculation pk
    pwcalc_avail = parameters["pp"]["pwcalc_avail"]
    aiida_node = orm.load_node(pwcalc_avail)

    # RemoteFolder
    remote_folder = aiida_node.outputs.remote_folder

    output_parameters = aiida_node.outputs.output_parameters.get_dict()

    # Orbitals
    lsda = parameters["pp"]["current_calc_lsda"]
    number_of_k_points = output_parameters["number_of_k_points"]

    lsign = parameters["pp"]["lsign"]

    # Fermi level
    if "fermi_energy" in output_parameters:
        fermi = output_parameters["fermi_energy"]
    else:
        fermi = output_parameters["fermi_energy_up"]

    # Parameters
    pp_parameters = {
        "charge_dens": {"spin_component": parameters["pp"]["charge_dens"]},
        "ildos": {
            "emin": parameters["pp"]["ildos_emin"] + fermi,
            "emax": parameters["pp"]["ildos_emax"] + fermi,
            "ildos_spin_component": parameters["pp"]["ildos_spin_component"],
        },
        "ldos_grid": {
            "emin": parameters["pp"]["ldos_emin"] + fermi,
            "emax": parameters["pp"]["ldos_emax"] + fermi,
            "delta_e": parameters["pp"]["ldos_delta_e"],
            "degauss_ldos": parameters["pp"]["degauss_ldos"],
            "use_gauss_ldos": parameters["pp"]["use_gauss_ldos"],
        },
        "stm": {
            "sample_bias": parameters["pp"]["stm_sample_bias"],
            "heights": parameters["pp"]["stm_heights"],
            "currents": parameters["pp"]["stm_currents"],
        },
        "wfn": {
            "orbitals": parse_list_of_tuples(
                parameters["pp"]["sel_orbital"], lsda, number_of_k_points
            ),
            "lsda": lsda,
            "number_of_k_points": number_of_k_points,
            "lsign": lsign,
        },
        "reduce_cube_files": parameters["pp"]["reduce_cube_files"],
        "ildos_stm": {
            "heights": parameters["pp"]["ildos_stm_heights"],
            "currents": parameters["pp"]["ildos_stm_currents"],
            "sample_bias": "",
        },
        "fermi": fermi,
    }
    properties = orm.List(list=properties_list)
    parameters = orm.Dict(dict=pp_parameters)
    builder = PPWorkChain.get_builder_from_protocol(
        parent_folder=remote_folder,
        pp_code=pp_code,
        critic2_code=critic2_code,
        python=python_code,
        parameters=parameters,
        properties=properties,
        structure=structure,
    )

    update_resources(builder, codes)

    return builder


workchain_and_builder = {
    "workchain": PPWorkChain,
    "get_builder": get_builder,
}
