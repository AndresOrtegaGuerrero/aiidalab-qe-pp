from aiida.engine import CalcJob
import os
from aiida import orm
from aiida.common import CalcInfo, CodeInfo


def create_file_content(input_file, parameters):
    # Construct the content using the dictionary values and the input file
    if "cells" in parameters:
        content = f"""crystal {input_file}
load {input_file}
stm {parameters['mode']} {parameters['value']} cells {parameters['cells'][0]} {parameters['cells'][1]}
"""
    else:
        content = f"""crystal {input_file}
load {input_file}
stm {parameters['mode']} {parameters['value']}
"""

    return content


class Critic2Calculation(CalcJob):
    """
    `CalcJob` implementation for the critic2 code.
    """

    _DEFAULT_INPUT_FILE = "aiida.in"
    _DEFAULT_OUTPUT_FILE = "aiida.out"
    _FILEOUT = "stdin_stm.dat"

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input(
            "ildos_filename",
            valid_type=orm.Str,
            default=orm.Str("aiida.fileout"),
            required=False,
            help="Name of the ILDOS file",
        )
        spec.input(
            "parent_folder",
            valid_type=(orm.RemoteData),
            required=True,
            help="Use a remote folder",
        )
        spec.input(
            "parameters",
            valid_type=orm.Dict,
            required=True,
            help="Input parameters",
        )
        spec.input(
            "metadata.options.input_filename",
            valid_type=str,
            default=cls._DEFAULT_INPUT_FILE,
        )
        spec.input(
            "metadata.options.output_filename",
            valid_type=str,
            default=cls._DEFAULT_OUTPUT_FILE,
        )
        spec.inputs["metadata"]["options"]["parser_name"].default = "critic2"
        spec.inputs["metadata"]["options"]["resources"].default = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }
        spec.inputs["metadata"]["options"]["withmpi"].default = False

        spec.output(
            "stm_data",
            valid_type=orm.ArrayData,
            required=True,
            help="STM data",
        )
        spec.exit_code(
            100,
            "ERROR_NO_REMOTE_FOLDER",
            message="The remote folder could not be accessed",
        )
        spec.exit_code(
            101,
            "ERROR_MISSING_OUTPUT_FILE",
            message="The output file was not found",
        )

    def prepare_for_submission(self, folder):
        # Prepare the input parameters
        parameters = self.inputs.parameters.get_dict()
        # Prepare the file with the ILDOS filename
        ildos_filename = "aiida.cube"
        # Write the input file
        input_filename = self.inputs.metadata.options.input_filename
        # Prerate the input file content
        file_content = create_file_content(ildos_filename, parameters)

        # Write the input file
        with folder.open(input_filename, "w") as infile:
            infile.write(file_content)

        remote_copy_list = []

        source = self.inputs.get("parent_folder", None)

        # Prepare the files to copy
        dirpath = os.path.join(
            source.get_remote_path(), self.inputs.ildos_filename.value
        )
        remote_copy_list.append((source.computer.uuid, dirpath, "aiida.cube"))

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = []
        codeinfo.stdin_name = self.inputs.metadata.options.input_filename
        codeinfo.stdout_name = self.inputs.metadata.options.output_filename
        codeinfo.code_uuid = self.inputs.code.uuid

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = remote_copy_list
        calcinfo.retrieve_list = [
            self._DEFAULT_OUTPUT_FILE,
            self._FILEOUT,
        ]

        return calcinfo
