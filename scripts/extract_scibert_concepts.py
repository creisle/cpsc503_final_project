"""
Load an Allennlp model and make predictions on a directory containing
PMC nXML files which have already been converted to plain text.

Code copied and modified from https://gitlab.com/TIBHannover/orkg/orkg-nlp.git

This code must be run with the model built and trained as described in the codebase linked above
"""
import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from glob import glob

import spacy
from allennlp.common import Params
from allennlp.data import DatasetReader
from allennlp.models import Model


def write_entities(entities):
    result = ""
    for i, e in enumerate(entities):
        result += e.to_standoff_str(i + 1)
    return result


def get_possible_labels(document):
    labels = []
    for sentence in document:
        for word in sentence:
            for l in word.labels:
                # remove prefix
                s = l.split("-")
                if len(s) == 2:
                    if not s[1] in labels:
                        labels.append(s[1])

    return labels


def sentences_to_entities(orig_text, sentences):
    result = []
    for label in get_possible_labels(sentences):
        entity_tokens = []
        for sentence in sentences:
            for token in sentence:
                if len(entity_tokens) > 0:
                    # inside of entitiy
                    if is_begin_of_label(token, label) or is_outside_of_label(token, label):
                        # end of entity
                        first_entity_token = entity_tokens[0]
                        last_entity_token = entity_tokens[-1]
                        if orig_text is None:
                            entity_text = " ".join([t.text for t in entity_tokens])
                        else:
                            entity_text = orig_text[
                                first_entity_token.start : last_entity_token.end
                            ]

                        result.append(
                            Entity(
                                label, first_entity_token.start, last_entity_token.end, entity_text
                            )
                        )

                        if is_begin_of_label(token, label):
                            # new entity started
                            entity_tokens = []
                            entity_tokens.append(token)
                        else:
                            # now outside of entity
                            entity_tokens = []
                    else:
                        # still inside of entity
                        entity_tokens.append(token)
                else:
                    # outside of entity
                    if is_begin_of_label(token, label) or is_inside_of_label(token, label):
                        # new entity started
                        entity_tokens = []
                        entity_tokens.append(token)
                    else:
                        # still outside
                        assert len(entity_tokens) == 0

        if len(entity_tokens) > 0:
            # finish entity
            first_entity_token = entity_tokens[0]
            last_entity_token = entity_tokens[-1]
            if orig_text is None:
                entity_text = " ".join([t.text for t in entity_tokens])
            else:
                entity_text = orig_text[first_entity_token.start : last_entity_token.end]

            result.append(
                Entity(label, first_entity_token.start, last_entity_token.end, entity_text)
            )

    return result


class Document:
    def __init__(self, sentences, text, basename):
        self.sentences = sentences
        self.text = text
        self.basename = basename

    def get_sentence_count(self):
        return len(self.sentences)


class Token:
    def __init__(self, labels=[], text='', start=-1, end=-1):
        self.labels = labels
        self.start = start
        self.end = end
        self.text = text

    def assign_new_labels(self, new_labels):
        return Token(new_labels, self.start, self.end, self.text)

    def get_token_of_type(self, token_type):
        for l in self.labels:
            if token_type in l:
                return l
        return None

    def __str__(self):
        if self.start < 0 and self.end < 0:
            return str(self.labels) + " " + self.text
        else:
            return str(self.labels) + " " + str(self.start) + " " + str(self.end) + " " + self.text

    def __repr__(self):
        return self.__str__()


def get_start_and_end_offset_of_token_from_spacy(token):
    start = token.idx
    end = start + len(token)
    return start, end


def get_sentences_and_tokens_from_spacy(text, spacy_nlp):
    """
    The max sentence length could be removed but would require retraining the model
    > Too many wordpieces, truncating sequence. If you would like a sliding window, set`truncate_long_sequences` to False
    """
    document = spacy_nlp(text)
    # sentences
    sentences = []
    spans = []
    for span in document.sents:
        sentence = [document[i] for i in range(span.start, span.end)]
        sentence_tokens = []
        sentence_spans = []
        for token in sentence:
            token_dict = {}
            token_dict['start'], token_dict['end'] = get_start_and_end_offset_of_token_from_spacy(
                token
            )
            token_dict['text'] = text[token_dict['start'] : token_dict['end']]
            if token_dict['text'].strip() in ['\n', '\t', ' ', '']:
                continue
            # Make sure that the token text does not contain any space
            if len(token_dict['text'].split(' ')) != 1:
                print(
                    "WARNING: the text of the token contains space character, replaced with hyphen\n\t{0}\n\t{1}".format(
                        token_dict['text'], token_dict['text'].replace(' ', '-')
                    )
                )
                token_dict['text'] = token_dict['text'].replace(' ', '-')
            sentence_tokens.append(token)
            sentence_spans.append((token_dict['start'], token_dict['end']))

        sentences.append(sentence_tokens)
        spans.append(sentence_spans)
    return sentences, spans


def load_bert_reader_model_experiment_dir(experiment_dir: str, cuda_device: int = -1):
    # check values of existing config
    config_file = os.path.join(experiment_dir, 'config.json')

    config = Params.from_file(config_file)

    # instantiate dataset reader
    print(config['dataset_reader'])
    reader = DatasetReader.from_params(config["dataset_reader"])

    # instantiate model w/ pretrained weights
    model = Model.load(
        config.duplicate(),
        weights_file=os.path.join(experiment_dir, 'best.th'),
        serialization_dir=experiment_dir,
        cuda_device=cuda_device,
    )

    # set training=false for prediction
    model.eval()

    return reader, model


def make_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def split_label(label_txt):
    if label_txt == 'O':
        bio = label_txt
        label = label_txt
    else:
        bio, label = label_txt.split('-')
    return bio, label


def extract_spans_with_allennlp(instances, spans, model, sentence_wise):
    s = time.time()

    predicted_labels = []
    outs = []
    print('extract spans with allennlp')
    chunks = list(make_chunks(instances, 64))
    print('predicting chunks: ' + str(len(chunks)), flush=True)
    for i, c in enumerate(chunks):
        print("Predicting chunk:" + str(i), flush=True)
        chunk_out = model.forward_on_instances(c)
        outs.extend(chunk_out)
    print('predicting chunks finished', flush=True)

    doc_likelihoods = None

    docs = []
    cdoc = None
    for i, (instance, sentence_spans, out) in enumerate(zip(instances, spans, outs)):
        pred_tags = out['tags']
        tokens = out['words']

        if "log_likelihood" in out:
            if doc_likelihoods is None:
                doc_likelihoods = []

            if sentence_wise:
                # document changed
                cur_doc = dict()
                cur_doc["id"] = str(i)
                cur_doc["sentences"] = []
                doc_likelihoods.append(cur_doc)

            log_likelihood = out["log_likelihood"]
            sent_info = dict()
            sent_info["n_tokens"] = len(tokens)
            sent_info["log_likelihood"] = log_likelihood
            sent_info["likelihood"] = math.exp(log_likelihood)
            sent_info["mnlp"] = log_likelihood / len(tokens)
            doc_likelihoods[-1]["sentences"].append(sent_info)

        assert len(pred_tags) == len(tokens)

        cdoc = Document([], None, i)
        docs.append(cdoc)

        sentence = []
        for token, token_span, pred_tag in zip(tokens, sentence_spans, pred_tags):
            bio, label = split_label(pred_tag)
            # map BIOUL to BIO
            if bio == 'U':
                bio = 'B'
            elif bio == 'L':
                bio = 'I'
            l = "O" if label == "O" else f'{bio}-{label}'
            start = token
            sentence.append(Token(labels=[l], text=token, start=token_span[0], end=token_span[1]))

            predicted_labels.append(label)
        cdoc.sentences.append(sentence)

    e = time.time()
    print(f'Time took for prediction: {e - s} sec')
    return docs, doc_likelihoods, predicted_labels


def load_pmc_text_file(filepath, reader):
    # the model the readme says they used. only need the tokenizer
    nlp = spacy.load("en_core_web_md", disable=['ner', 'tagger', 'parser'])
    # split document into sentences
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    instances = []
    with open(filepath, 'r') as fh:
        sentences, spans = get_sentences_and_tokens_from_spacy(fh.read().strip(), nlp)
        return [reader.text_to_instance(d) for d in sentences], spans


parser = argparse.ArgumentParser()
parser.add_argument('--gpu', action='store_true', default=False, help='use GPU')
parser.add_argument(
    '--input_dir',
    type=str,
    help='Location of text *.nxml.txt files to be classified',
    required=True,
)
parser.add_argument(
    '--output_dir',
    type=str,
    help='Output dir to dump predicted .nxml.txt.ann file',
    required=True,
)
parser.add_argument(
    '--experiment_dir',
    help='path to the folder for the model we want to use',
    default='results/stm_v2_best_models/stm_run_2019-05-08_stm_v2_overall/stm_fold_4_dr_0.5_lstm_hs_768_lr_0.001',
)
args = parser.parse_args()

# dataset reader code: https://github.com/allenai/allennlp/blob/master/allennlp/data/dataset_readers/conll2003.py
reader, model = load_bert_reader_model_experiment_dir(
    experiment_dir=args.experiment_dir,
    cuda_device=0 if args.gpu else -1,  # for some reason 0 means yes use GPU, use -1 to turn off
)
# read instances for prediction
print("loading data (allen)...", flush=True)

input_files = glob(os.path.join(args.input_dir, '*.nxml.txt'))

errors = []

for i, text_file in enumerate(input_files):
    basename = os.path.basename(text_file)
    output_file = os.path.join(args.output_dir, f'{basename}.ann')

    if os.path.exists(output_file):
        print('skipping. exists:', output_file)
        continue

    try:
        print(f'reading {i + 1} / {len(input_files)}:', text_file)
        instances, spans = load_pmc_text_file(text_file, reader)

        # # predict while aligning read spans with each token
        docs, doc_likelihoods, token_predicted_labels = extract_spans_with_allennlp(
            instances, spans, model, False
        )

        # write in `.ann` format
        print('writing:', output_file)
        with open(output_file, 'w', encoding="utf-8") as f_out:
            for d in docs:
                entities = sentences_to_entities(orig_text=None, sentences=d.sentences)
                entities_text = write_entities(entities)
                f_out.write(entities_text)
    except Exception as err:
        print(err, file=sys.stderr)
        errors.append(err)

if errors:
    print(f'encountered {len(errors)} errors', file=sys.stderr)
stamp = os.path.join(args.output_dir, 'SCIBERT_ANNOTATIONS.COMPLETE')
print('writing:', stamp)
with open(stamp, 'w') as fh:
    fh.write(f'total files: {len(input_files)}\n')
    fh.write(f'completed: {len(input_files) - len(errors)}\n')
    fh.write(f'errors: {len(errors)}\n\n')
    for error in errors:
        fh.write(str(error) + '\n\n')
