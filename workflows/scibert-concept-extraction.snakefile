"""
Runs the concept extraction script
"""

import os
from glob import glob

batches = []

# change the below to match where you have stored the trained model
MODEL_DIR = 'results/stm_v2_best_models/stm_run_2019-05-08_stm_v2_overall/stm_fold_4_dr_0.5_lstm_hs_768_lr_0.001'
# CHANGE below depending on the python required by your cluster nodes
# this is the python which must have the requirements.scibert.txt dependencies installed
# note that this was run on ubuntu
SLURM_PYTHON='/projects/creisle_prj/datasets/orkg-nlp/STM-corpus/venv3.7/bin/python'
DATA_DIR = 'data/pmc_articles'
batches_file = 'batches.txt'

if os.path.exists(batches_file):
    print('reading:', batches_file)
    with open(batches_file, 'r') as fh:
        batches = [p.strip() for p in fh.readlines() if p.strip()]
else:
    print('gathering batches')
    for batch in glob(f'{DATA_DIR}/*'):
        if os.path.isdir(batch):
            batch_id = batch.split('/')[-1]

            if os.path.exists(os.path.join(batch, 'NXML_TXT.COMPLETE')):
                batches.append(batch_id)
    print('writing:', batches_file)
    with open(batches_file, 'w') as fh:
        fh.write('\n'.join(batches))
print('found', len(batches), 'batches')
batches = sorted(batches)[:-100]

rule all:
    input: expand(DATA_DIR + '/{batch_id}/SCIBERT_ANNOTATIONS.COMPLETE', batch_id=batches)

rule scibert_annotations:
    resources:
        gpus=1,
        log_dir='logs',
        mem_mb=7900,
        time_limit='2-0'
    output: DATA_DIR + '/{batch_id}/SCIBERT_ANNOTATIONS.COMPLETE'
    log:  'snakemake_logs/{batch_id}.snakemake.scibert_annotations.log'
    shell: SLURM_PYTHON + ' extract_scibert_concepts.py --gpu '
        + ' --input_dir "' + DATA_DIR + '/{wildcards.batch_id}"'
        + ' --experiment_dir ' + MODEL_DIR
        + ' --output_dir "' + DATA_DIR + '/{wildcards.batch_id}" &> "{log}"'
