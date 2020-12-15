import argparse
import os
import re

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


def read_csv(filepath):
    print('reading:', filepath)
    return pd.read_csv(filepath)


def parse_log(log):
    """
    Parse the output of the log file created during model training
    """
    result_df = None
    current_block = None
    current_df = None

    print('reading:', log)
    with open(log, 'r') as fh:
        for i, line in enumerate(fh.readlines()):
            if re.search(
                r'.*allennlp\.training\.tensorboard_writer\s*-\s*Training\s*\|\s*Validation', line
            ):
                current_block = []
                current_df = None
            elif current_block is not None:
                m = re.match(r'.*allennlp\.training\.tensorboard_writer\s*-(.*)', line)
                if m:
                    metric, training, validation = (t.strip() for t in m.group(1).split('|'))
                    if 'memory_MB' not in metric:
                        current_block.append((metric, 'training', training))
                        current_block.append((metric, 'validation', validation))
                else:
                    m = re.search(
                        r'.*allennlp.training.checkpointer -.*Copying weights to \'results/stm_run_[^/]+_stm_v\d+_(?P<domain>[A-Za-z0-9-_]+)/stm_fold_(?P<fold>\d+)_dr_(?P<dropout>\d+\.\d+)_lstm_hs_(?P<hs>\d+)_lr_(?P<lr>\d+\.\d+)/best.th',
                        line,
                    )

                    if m:
                        df = pd.DataFrame(
                            current_block, columns=['metric', 'stage', 'metric_value']
                        )
                        df = pd.pivot_table(
                            df,
                            columns=['metric'],
                            index=['stage'],
                            values='metric_value',
                            aggfunc='first',
                        ).reset_index()
                        df = df.replace('N/A', np.nan)
                        df['fold'] = int(m.group('fold'))
                        df['dropout'] = float(m.group('dropout'))
                        df['learning_rate'] = float(m.group('lr'))
                        df['hs'] = int(m.group('hs'))
                        df['domain'] = m.group('domain')
                        current_df = df
                    current_block = None
            elif current_df is not None:
                m = re.search(r'Epoch (\d+)/\d+', line)

                if m:
                    current_df['epoch'] = int(m.group(1))
                    if result_df is None:
                        result_df = current_df
                    else:
                        result_df = pd.concat([result_df, current_df])
    return result_df


parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_file',
    help='model training log file',
    default='/projects/creisle_prj/datasets/orkg-nlp/STM-corpus/model_logs/slurm_96952.log',
)
parser.add_argument(
    '--output',
    help='path the the directory to output plots to',
    default=relative_file('../results'),
)
args = parser.parse_args()

sns.set_style('whitegrid')


def savefig(ax, plot_name):
    plot_name = os.path.join(args.output, plot_name)
    print('writing:', plot_name)
    try:
        ax.figure.savefig(plot_name, bbox_inches='tight')
    except AttributeError:
        ax.savefig(plot_name, bbox_inches='tight')
    plt.close()


output_file = os.path.join(args.output, 'training_log_data.csv')
if not os.path.exists(output_file):
    df = parse_log(args.input_file)

    print('writing:', output_file)
    df.to_csv(output_file, index=False)
else:
    df = read_csv(output_file)

fig = sns.relplot(
    kind='line', data=df, x='epoch', y='f1-measure-overall', hue='stage', col='domain', col_wrap=4
)
savefig(fig, 'scibert.training_log.all.f1.png')
fig = sns.relplot(kind='line', data=df, x='epoch', y='loss', hue='stage', col='domain', col_wrap=4)
savefig(fig, 'scibert.training_log.all.loss.png')

df = df[df.domain == 'overall']
df = pd.melt(
    df,
    id_vars=['stage', 'learning_rate', 'hs', 'dropout', 'epoch', 'fold'],
    value_vars=[
        'recall-overall',
        'precision-overall',
        'f1-measure-overall',
        'accuracy',
    ],
    var_name='measure',
)
print(df)
df['model'] = df[['learning_rate', 'hs', 'dropout']].apply(
    lambda row: '/'.join(str(col) for col in row), axis=1
)

fig = sns.relplot(
    kind='line', data=df, x='epoch', y='value', hue='stage', col='measure', col_wrap=2
)
savefig(fig, 'scibert.training_log.overall.png')
