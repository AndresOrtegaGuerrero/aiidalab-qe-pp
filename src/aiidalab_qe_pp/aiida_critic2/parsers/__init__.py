from aiida.common import NotExistent, OutputParsingError
from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory
from aiida.orm import ArrayData
import numpy as np

Critic2Calculation = CalculationFactory("critic2")


class Critic2Parser(Parser):
    """
    Parser class for parsing output of critic2.
    """

    def parse(self, **kwargs):
        """Parse the retrieved files from a critic2 calculation."""

        try:
            out_folder = self.retrieved
        except NotExistent:
            self.logger.error("No retrieved folder found")
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        list_of_files = out_folder.base.repository.list_object_names()

        data_file = self.node.process_class._FILEOUT
        output_file = self.node.process_class._DEFAULT_OUTPUT_FILE

        if data_file not in list_of_files:
            self.logger.error(f"Output file {output_file} not found")
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILE

        finished = False
        with out_folder.open(output_file) as file:
            for line in file.readlines():
                if "CRITIC2 ended successfully" in line:
                    finished = True

        if not finished:
            raise OutputParsingError("Calculation did not finish correctly")

        xcryst, ycryst, xcart, ycart, fstm = read_stm_file(out_folder, data_file)

        stm_data = ArrayData()
        stm_data.set_array("xcryst", np.array(xcryst))
        stm_data.set_array("ycryst", np.array(ycryst))
        stm_data.set_array("xcart", np.array(xcart))
        stm_data.set_array("ycart", np.array(ycart))
        stm_data.set_array("fstm", np.array(fstm))
        self.out("stm_data", stm_data)

        return ExitCode(0)

        return ExitCode(0)


def read_stm_file(out_folder, data_file):
    xcryst = []
    ycryst = []
    xcart = []
    ycart = []
    fstm = []

    with out_folder.open(data_file) as file:
        for line in file:
            # Skip lines that start with ##
            if line.startswith("##"):
                continue

            # Split the line into columns and convert to float
            columns = line.split()
            if len(columns) == 5:
                xcryst.append(float(columns[0]))
                ycryst.append(float(columns[1]))
                xcart.append(float(columns[2]))
                ycart.append(float(columns[3]))
                fstm.append(float(columns[4]))

    return xcryst, ycryst, xcart, ycart, fstm
