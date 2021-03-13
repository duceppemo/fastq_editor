# fastq_editor
Prepend or append a specified sequence to all entries in fastq files in a folder
```
usage: fastq_editor.py [-h] -i /input_folder/ -o /modified_fastq/ -m
                       prepend|append -s ATCGATCGATCGATCG

Prepend or append every entry of a fastq file wiht a specific sequence. Only
works with phred 33 fastq files.

optional arguments:
  -h, --help            show this help message and exit
  -i /input_folder/, --input /input_folder/
                        Input folder with fastq file(s), gzipped or not
  -o /modified_fastq/, --output /modified_fastq/
                        Output folder
  -m prepend|append, --mode prepend|append
                        "prepend" (before) or "append" (after)
  -s ATCGATCGATCGATCG, --sequence ATCGATCGATCGATCG
                        Sequence string to prepend or append
```
