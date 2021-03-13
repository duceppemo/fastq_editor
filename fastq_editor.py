#!/usr/local/env python3

import os
import gzip
import pathlib
from argparse import ArgumentParser


__author__ = 'duceppemo'
__version__ = '0.1'


class FastqEditor(object):
    def __init__(self, args):
        # Get options
        self.args = args
        self.input_folder = args.input
        self.output_folder = args.output
        self.mode = args.mode
        self.seq = args.sequence

        # Dictionary to store all the fastq file(s)
        self.master_dict = dict()

        # Run
        self.run()

    def run(self):
        """
        This is where all the main program parts are being called
        :return:
        """
        # Run all checks to make sure the script runs smoothly
        self.checks()
        # Create a list of all the fastq files in the input folder
        fastq_list = FastqEditor.list_fastq(self.input_folder)
        # Process each fastq file and save info in a dictionary (files) of dictionaries (reads)
        for fq in fastq_list:
            self.master_dict[fq] = FastqEditor.parse_fastq(fq)
        # Write the modified output fastq files
        FastqEditor.write_modified_fastq(self.master_dict, self.seq, self.mode, self.output_folder)

    def checks(self):
        """
        Check if all options have been filled properly
        :return:
        """
        # Check mode
        if not self.mode:
            raise Exception('Please choose "prepend" or "append" mode')

        # Check input folder
        if not os.path.exists(self.input_folder):
            raise Exception('Input folder does not exists')
        if not os.path.isdir(self.input_folder):
            raise Exception('Input is not a folder')

        # Check output folder
        if self.output_folder == self.input_folder:
            raise Exception('Please choose a different output folder than the input folder')
        if not os.path.exists(self.output_folder):
            FastqEditor.make_folder(self.output_folder)  # Create output folder is does not exists already

    @staticmethod
    def list_fastq(my_path):
        """
        Walk input directory and list all the fastq files. Accepted file extensions are '.fastq', '.fastq.gz',
        '.fq' and '.fq.gz'.
        :param my_path: string. Input folder path
        :return: list of strings. Fastq files in input folder
        """
        # Create empty list to hold the file paths
        fastq_list = list()
        # Walk the input directory recursively and look for fastq files
        for root, directories, filenames in os.walk(my_path):
            for filename in filenames:
                absolute_path = os.path.join(root, filename)
                if os.path.isfile(absolute_path) and filename.endswith(('.fastq', '.fastq.gz', '.fq', '.fq.gz')):
                    fastq_list.append(absolute_path)  # Add fastq file path to the list
        return fastq_list

    @staticmethod
    def parse_fastq(fastq):
        """
        Parse fastq file into a dictionary
        :param fastq: string. Input fastq file path
        :return: dictionary. {header: [sequence, quality]}
        """
        with gzip.open(fastq, 'rb') if fastq.endswith('.gz') else open(fastq, 'r') as f:
            counter = 0
            header = ''
            seq = ''
            qual = ''
            fastq_dict = dict()

            for line in f:
                counter += 1
                if fastq.endswith('.gz'):
                    line = line.decode('ascii')  # Convert to ASCII if files were gzipped (binary)
                line = line.rstrip()

                if counter == 1:  # Header line line
                    if not line.startswith('@'):  # first line of 4 should always start with "@"
                        raise Exception('Fastq file invalid.')
                    header = line
                elif counter == 2:  # Sequence line
                    seq = line
                elif counter == 3:  # that's the "+" line, we can skip it
                    pass
                elif counter == 4:  # Quality line
                    qual = line
                    fastq_dict[header] = [seq, qual]  # Store the fastq entry in the dictionary
                    counter = 0  # Reset counter because each fastq entry in a file always have 4 lines

            return fastq_dict

    @staticmethod
    def write_modified_fastq(master_dict, seq_to_add, mode, outfolder):
        """

        :param master_dict: dictionary. Contains files and reads info
        :param seq_to_add: string. Sequence to add
        :param mode: string. Prepend or append
        :param outfolder: string. Path of output folder
        :return:
        """
        for f, fastq_dict in master_dict.items():
            # Get file and reads info back
            (h, seq_info) = fastq_dict.items()
            header = h[0]
            seq = seq_info[1][0]
            qual = seq_info[1][1]
            # Generate corresponding quality (F = Phred 40)
            qual_to_add = 'F' * len(seq_to_add)
            # Create file path of output file
            outfile = outfolder + '/' + os.path.basename(f)
            # Since all output files are gzipped, make sure to add ".gz" extensions to the input files
            # that were not compressed
            if not outfile.endswith('.gz'):
                outfile += '.gz'

            # Add sequence to fastq entry and write to gzipped output file
            with gzip.open(outfile, 'wb') as out_f:
                if mode == 'prepend':
                    # Convert to binary for gzipped
                    out_f.write('{}\n{}{}\n{}\n{}{}\n'.format(header, seq_to_add, seq, '+', qual_to_add, qual).encode())
                else:  # if mode == 'append':
                    # Convert to binary for gzipped
                    out_f.write('{}\n{}{}\n{}\n{}{}\n'.format(header, seq, seq_to_add, '+', qual, qual_to_add).encode())

    @staticmethod
    def make_folder(folder):
        """
        Create output folder.
        :param folder: string. Output folder path.
        :return:
        """
        # Will create parent directories if don't exist and will not return error if already exists
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    parser = ArgumentParser(description='Prepend or append every entry of a fastq file wiht a specific sequence.'
                                        ' Only works with Phred 33 fastq files.')
    parser.add_argument('-i', '--input', metavar='/input_folder/',
                        required=True,
                        type=str,
                        help='Input folder with fastq file(s), gzipped or not. '
                             'Accepted file extensions are ".fastq", ".fastq.gz", ".fq" and ".fq.gz". '
                             'Will look for files recursively. '
                             'Mandatory.')
    parser.add_argument('-o', '--output', metavar='/modified_fastq/',
                        required=True,
                        help='Output folder. Must be different than input folder. '
                             'Mandatory.')
    parser.add_argument('-m', '--mode', metavar='prepend|append',
                        required=True,
                        type=str,
                        help='"prepend" (before) or "append" (after). '
                             'Mandatory.')
    parser.add_argument('-s', '--sequence', metavar='ATCGATCGATCGATCG',
                        required=True,
                        type=str,
                        help='Sequence string to prepend or append. '
                             'Mandatory.')

    # Get the arguments into an object
    arguments = parser.parse_args()

    FastqEditor(arguments)
