import os

import pandas as pd
import numpy as np
import csv 
from matplotlib import pyplot as plt

def loadCoherenceData(path):
    with open(path) as csvFile:
        inCSV = csv.reader(csvFile, delimiter=',')
        lsaHeader = "lsa_2_all_para"
        ldaHeader = "lda_2_all_para"

        lsaVals = []
        ldaVals = []
        lsaIndex = 0
        ldaIndex = 0

        rowNum = 0   
        for row in inCSV:

            if rowNum > 0:
                lsa = float(row[lsaIndex])
                lda = float(row[ldaIndex])

                if lsa > 0.0:
                    lsaVals.append(float(row[lsaIndex]))
                
                if lda > 0.0:
                    ldaVals.append(float(row[ldaIndex]))
                    
            else:
                headers = row
                for i in range(len(headers)):
                    if headers[i] == lsaHeader:
                        lsaIndex = i

                    elif headers[i] == ldaHeader:
                        ldaIndex = i

            rowNum += 1

              
        return {"lsa": np.array(lsaVals), "lda": np.array(ldaVals)}



#Creates a histogram based on the scores and saves it to outPath.
def saveHistogram(scores, title, outPath, bins=20):
    df = pd.DataFrame({title: scores})
    hist = df.hist(bins=bins)
    fig = hist[0][0].get_figure()
    fig.savefig(outPath + "/" + title + ".png")       
        



coherencePath = "../results/taaco_scores.csv"
figPath = "../results/taaco_plots"

data = loadCoherenceData(coherencePath)


saveHistogram(data["lsa"], "LSA Scores", figPath)
saveHistogram(data["lda"], "LDA Scores", figPath) 

print("Plotted LDA and LSA data from " + figPath)
