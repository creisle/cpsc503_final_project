from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.test.utils import datapath
from gensim.models import LdaModel
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess

import regex
import argparse
import gensim
import spacy
import os
import pandas as pd




def preProcess(text):
    #Lemmatization
    sp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

    text = regex.sub('[,\.!?]', '', text)
    text = text.lower()

    words = gensim.utils.simple_preprocess(text, deacc=True) #Tokenize
    
    data = [words]
    
    # Build the bigram model
    bi = gensim.models.Phrases(data, min_count=5, threshold=100) 
    bi_mod = gensim.models.phrases.Phraser(bi)
    
    #Remove stopwords
    sWords = sp.Defaults.stop_words
    
    lim = len(words)
    i = 0
    for w in words:
        if words[i] in sWords:
            words.pop(i)
            lim = len(words)
        
        i += 1
        if i >= lim:
            break
            
            
    word_bigrams = [bi_mod[data[0]]]
    
    
        
    lemmatizedText = []
    
    spacyLemmas = sp(" ".join(word_bigrams[0])) 
    permit = ['NOUN', 'ADJ', 'VERB', 'ADV']
    
    for t in spacyLemmas:
        if t.pos_ in permit:
            lemmatizedText.append(t.lemma_)
    
    
    return [lemmatizedText]



def calcCoherence(lemmatizedTexts, passes=100, nTopics=5):
    
    id2word = Dictionary(lemmatizedTexts)
    corp = [id2word.doc2bow(text) for text in lemmatizedTexts]
    
    ldaModel = gensim.models.LdaMulticore(corpus=corp,
                                       id2word=id2word,
                                       num_topics=nTopics, 
                                       passes=passes,
                                       random_state=100,
                                       per_word_topics=False,
                                       alpha=0.01,
                                       eta=0.9)
    
    coherenceModel = CoherenceModel(model=ldaModel, 
                                        texts=lemmatizedTexts, 
                                        dictionary=id2word, 
                                        coherence='c_v',
                                        processes = 0)
    
    return coherenceModel.get_coherence()
        

    
def outputScoreData(score, docName, outFile):
    df = pd.DataFrame(
        [[docName, "lda_coherence", score]],
        columns=["filename", "measure", "score"]
    )
        
    if(outFile != ""):
        with open(outFile, "w") as fh:
            fh.write(df.to_csv(sep='\t', index=False))
    



parser = argparse.ArgumentParser()
parser.add_argument('--in_file', help='the input txt file with paper content', default="./test.txt")
parser.add_argument('--out_file', help='the output file for results', default="./lda_scores.tsv")
parser.add_argument('--passes', help='number of passes over texts', default="100")
parser.add_argument('--topics', help='number of topics to consider', default="5")

args = parser.parse_args()

if not os.path.exists(args.in_file):
    raise FileNotFoundError(args.in_file)

inFile = args.in_file
outFile = args.out_file
passes = int(args.passes)
nTopics = int(args.topics)

ldaCoherence = 0.0

with open(inFile, "r", encoding='utf-8') as pFile:
    text = pFile.read()
    lemmatizedText = preProcess(text)
    ldaCoherence = calcCoherence(lemmatizedText, passes, nTopics)
     
    print (ldaCoherence)
outputScoreData(ldaCoherence, os.path.basename(inFile), outFile)

