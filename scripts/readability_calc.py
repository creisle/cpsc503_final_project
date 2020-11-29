import os
import regex
import textstat
import argparse

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt



#Calculates the Flesch-Kincaid Grade Level, Gunning FOG Index, Automated Readability Index and Coleman-Liau Index
#for the given text. Writes results to an outpul tsv file.
def calcReadabilityScores(content, basename, stats=[], outFile=""):
    
    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(content),
        "gunning_fog": textstat.gunning_fog(content),
        "automated_readability_index": textstat.automated_readability_index(content),
        "coleman_liau_index": textstat.coleman_liau_index(content)
    }

    for metric in scores:
        if scores[metric] > 0.0:                                        #Ignore scores that are 0, as this is an error.
            stats.append([basename, metric, scores[metric]])
    

    

#Creates a histogram based on the scores and saves it to outPath.
def saveHistogram(scores, title, outPath, bins=20):
    df = pd.DataFrame({title: scores})
    hist = df.hist(bins=bins)
    fig = hist[0][0].get_figure()
    fig.savefig(outPath + "/" + title + ".png")
    
    

def outputScorePlots(data, outPath):
    #fleschScores = gunningScores = automatedScores = colemanScores = []
    scores = {"flesch_reading_ease": np.array([]), 
              "gunning_fog": np.array([]),  
              "automated_readability_index": np.array([]), 
              "coleman_liau_index": np.array([])
             }
    
    #Get all the scores for each metric
    for row in data:
        measure = row[1]
        score = row[2]
        
        for key in scores:
            if (measure == key):
                scores[key] = np.append(scores[key], score)
                
                
    #Plot scores for each score with a bar chart
    for key in scores:
        saveHistogram(scores[key], key, outPath)
    


def outputScoreData(data, outFile):
    df = pd.DataFrame(
        data,
        columns=["filename", "measure", "score"]
    )
        
    if(outFile != ""):
        with open(outFile, "w") as fh:
            fh.write(df.to_csv(sep='\t', index=False))
       
        



parser = argparse.ArgumentParser()
parser.add_argument(
    '--papers_dir',
    help='glob pattern to use in finding text files. MUST be quoted to avoid expanding beforehand',
    default="D:/pmc_archive/pmc_txt"
)
parser.add_argument(
    '--out_file',
    help='path the the TSV output file',
    default="../results/textstat.results.tsv"
)

parser.add_argument(
    '--fig_path',
    help='path to the output figure dir',
    default="../results/textstat_plots"
)

args = parser.parse_args()


#For each paper in papersDir, calc readibility scores and aggregate scores for analysis
stats = []
papersDir = args.papers_dir
outFile = args.out_file
figPath = "../results/textstat_plots"

papers = os.listdir(papersDir)

for p in papers:
    with open(papersDir + "/" + p, "r", encoding='utf-8') as pFile:
        text = pFile.read()
        calcReadabilityScores(content=text, basename=p, stats=stats, outFile=outFile)
        print("calculating readability scores for " + p)


outputScoreData(stats, outFile)
outputScorePlots(stats, figPath)




