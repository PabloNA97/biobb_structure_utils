#!/usr/bin/env python3

"""Module containing the ExtractChain class and the command line interface."""
import argparse
from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools.file_utils import launchlogger
from biobb_structure_utils.utils.common import *


class ExtractChain(BiobbObject):
    """
    | biobb_structure_utils ExtractAtoms
    | This class is a wrapper of the Structure Checking tool to extract a chain from a 3D structure.
    | Wrapper for the `Structure Checking <https://github.com/bioexcel/biobb_structure_checking>`_ tool to extract a chain from a 3D structure.

    Args:
        input_structure_path (str): Input structure file path. File type: input. `Sample file <https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/data/utils/extract_chain.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_structure_path (str): Output structure file path. File type: output. `Sample file <https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/reference/utils/ref_extract_chain.pdb>`_. Accepted formats: pdb (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **chains** (*list*) - (None) List of chains to be extracted from the input_structure_path file. If empty, all the chains of the structure will be returned.
            * **check_structure_path** (*string*) - ("check_structure") path to the check_structure application
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_structure_utils.utils.extract_chain import extract_chain
            prop = { 
                'chains': [ 'A', 'B' ] 
            }
            extract_chain(input_structure_path='/path/to/myStructure.pdb, 
                        output_structure_path='/path/to/newStructure.pdb', 
                        properties=prop)

    Info:
        * wrapped_software:
            * name: Structure Checking from MDWeb
            * version: >=3.0.3
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_structure_path, output_structure_path, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)

        # Input/Output files
        self.io_dict = {
            "in": {"input_structure_path": input_structure_path},
            "out": {"output_structure_path": output_structure_path}
        }

        # Properties specific for BB
        self.check_structure_path = properties.get('check_structure_path', 'check_structure')
        self.chains = properties.get('chains', [])
        self.properties = properties

        # Check the properties
        self.check_properties(properties)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`ExtractChain <utils.extract_chain.ExtractChain>` utils.extract_chain.ExtractChain object."""

        self.io_dict['in']['input_structure_path'] = check_input_path(self.io_dict['in']['input_structure_path'],
                                                                      self.out_log, self.__class__.__name__)
        self.io_dict['out']['output_structure_path'] = check_output_path(self.io_dict['out']['output_structure_path'],
                                                                         self.out_log, self.__class__.__name__)

        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # check if user has passed chains properly
        chains = check_format_chains(self.chains, self.out_log)

        # run command line
        self.cmd = [self.check_structure_path,
                    '-i', self.io_dict['in']['input_structure_path'],
                    '-o', self.io_dict['out']['output_structure_path'],
                    '--force_save',
                    'chains', '--select', chains]

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))
        self.remove_tmp_files()

        return self.return_code


def check_format_chains(chains, out_log):
    """ Check format of chains list """
    if not chains:
        fu.log('Empty chains parameter, all chains will be returned.', out_log)
        return 'All'

    if not isinstance(chains, list):
        fu.log('Incorrect format of chains parameter, all chains will be returned.', out_log)
        return 'All'

    return ','.join(chains)


def extract_chain(input_structure_path: str, output_structure_path: str, properties: dict = None, **kwargs) -> int:
    """Execute the :class:`ExtractChain <utils.extract_chain.ExtractChain>` class and
    execute the :meth:`launch() <utils.extract_chain.ExtractChain.launch>` method."""

    return ExtractChain(input_structure_path=input_structure_path, 
                        output_structure_path=output_structure_path,
                        properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Extract a chain from a 3D structure.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-i', '--input_structure_path', required=True, help="Input structure file path. Accepted formats: pdb.")
    required_args.add_argument('-o', '--output_structure_path', required=True, help="Output structure file path. Accepted formats: pdb.")

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    extract_chain(input_structure_path=args.input_structure_path, 
                  output_structure_path=args.output_structure_path,
                  properties=properties)


if __name__ == '__main__':
    main()