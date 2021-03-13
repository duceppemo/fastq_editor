#!/usr/local/env python3

import os
import gzip
import pathlib
from argparse import ArgumentParser


__author__ = 'duceppemo'
__version__ = '0.1'


class FastqEditor(object):
    def __init__(self, args):
        self.args = args
        self.input_folder = args.input
        self.output_folder = args.output
        self.mode = args.mode
        self.seq = args.sequence

        # data
        self.master_dict = dict()

        # Run
        self.run()

    def run(self):
        self.checks()
        fastq_list = FastqEditor.list_fastq(self.input_folder)
        fastq_dict = dict()
        for fq in fastq_list:
            fastq_dict.update(FastqEditor.parse_fastq(fq))
            self.master_dict[fq] = fastq_dict
        FastqEditor.write_modified_fastq(self.master_dict, self.seq, self.mode, self.output_folder)

    def checks(self):
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
            FastqEditor.make_folder(self.output_folder)

    @staticmethod
    def list_fastq(mu_path):
        fastq_list = list()
        for root, directories, filenames in os.walk(mu_path):
            for filename in filenames:
                absolute_path = os.path.join(root, filename)
                if os.path.isfile(absolute_path) and filename.endswith(('.fastq', '.fastq.gz', '.fq', '.fq.gz')):
                    fastq_list.append(absolute_path)
        return fastq_list

    @staticmethod
    def parse_fastq(fastq):
        with gzip.open(fastq, 'rb') if fastq.endswith('.gz') else open(fastq, 'r') as f:
            counter = 0
            header = ''
            seq = ''
            qual = ''
            fastq_dict = dict()

            for line in f:
                counter += 1
                if fastq.endswith('.gz'):
                    line = line.decode('ascii')
                line = line.rstrip()

                if counter == 1:
                    if not line.startswith('@'):
                        raise Exception('Fastq file invalid')
                    header = line
                elif counter == 2:
                    seq = line
                elif counter == 3:
                    pass
                elif counter == 4:
                    qual = line
                    fastq_dict[header] = [seq, qual]
                    counter = 0

            return fastq_dict

    @staticmethod
    def write_modified_fastq(master_dict, seq_to_add, mode, outfolder):
        for f, fastq_dict in master_dict.items():
            (h, seq_info) = fastq_dict.items()
            header = h[0]
            seq = seq_info[1][0]
            qual = seq_info[1][1]
            qual_to_add = 'F' * len(seq_to_add)
            outfile = outfolder + '/' + os.path.basename(f)
            if not outfile.endswith('.gz'):
                outfile += '.gz'
            with gzip.open(outfile, 'wb') as out_f:
                if mode == 'prepend':
                    out_f.write('{}\n{}{}\n{}\n{}{}\n'.format(header, seq_to_add, seq, '+', qual_to_add, qual).encode())
                else:  # if mode == 'append':
                    out_f.write('{}\n{}{}\n{}\n{}{}\n'.format(header, seq, seq_to_add, '+', qual, qual_to_add).encode())

    @staticmethod
    def make_folder(folder):
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    parser = ArgumentParser(description='Prepend or append every entry of a fastq file wiht a specific sequence.'
                                        ' Only works with phred 33 fastq files.')
    parser.add_argument('-i', '--input', metavar='/input_folder/',
                        required=True,
                        type=str,
                        help='Input folder with fastq file(s), gzipped or not')
    parser.add_argument('-o', '--output', metavar='/modified_fastq/',
                        required=True,
                        help='Output folder')
    parser.add_argument('-m', '--mode', metavar='prepend|append',
                        required=True,
                        type=str,
                        help='"prepend" (before) or "append" (after)')
    parser.add_argument('-s', '--sequence', metavar='ATCGATCGATCGATCG',
                        required=True,
                        type=str,
                        help='Sequence string to prepend or append')

    # Get the arguments into an object
    arguments = parser.parse_args()

    FastqEditor(arguments)
    
