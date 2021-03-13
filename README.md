# fastq_editor
Prepend or append a specified sequence to all entries in fastq files in a folder
```
usage: fastq_editor.py [-h] -i /input_folder/ -o /modified_fastq/ -m prepend|append -s ATCGATCGATCGATCG

Prepend or append every entry of a fastq file with a specific sequence. Only works with Phred 33 fastq files.

optional arguments:
  -h, --help            show this help message and exit
  -i /input_folder/, --input /input_folder/
                        Input folder with fastq file(s), gzipped or not. Accepted file extensions are ".fastq", ".fastq.gz", ".fq" and ".fq.gz". Will look for files
                        recursively. Mandatory.
  -o /modified_fastq/, --output /modified_fastq/
                        Output folder. Must be different than input folder. Mandatory.
  -m prepend|append, --mode prepend|append
                        "prepend" (before) or "append" (after). Mandatory.
  -s ATCGATCGATCGATCG, --sequence ATCGATCGATCGATCG
                        Sequence string to prepend or append. Mandatory.

```
