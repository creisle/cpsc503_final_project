import pandas as pd 
import argparse
import os





def relative_file(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)



def isEng(locale):
    engGroups = ['US', 'UK', 'Canada', 'Australia']
   
    if locale in engGroups:
        return True

    return False



def isEngReview(pmid, mappingsArr):
    mapping = None
    
    result = mappingsArr[mappingsArr[:, 1] == pmid]
    
    if len(result) > 0:
        mapping = result[0]

    if mapping is not None:
        if mapping[2] == "review" and isEng(mapping[5]): 
            print("true")
            return True

    print("false")
    return False



def splitGroups(scoreDF, pmidMappings, maxRows = 5000000):
    groups = {
        "eng_review": [],
        "esl_nonreview": []
    }
    

    engReviewIDs = []
    
   
    for row in pmidMappings.itertuples():
        if row.pubtype == "review" and isEng(row.country): 
            engReviewIDs.append(row.PMCID)

    scoreTuples = scoreDF.itertuples() 
    i = 0
    for score in scoreTuples:
        if i > maxRows:
            break
        i += 1
        pmcid = score.filename.split(".")[0]
        print ("Processing %s - %d processed" % (pmcid, i))
        #If this score belongs to English Review group
        if pmcid in engReviewIDs:  #isEngReview(pmid, mappings): 
            groups["eng_review"].append(score)
 
        #Otherwise, add it to the ESL non-review group
        else:
            groups["esl_nonreview"].append(score)

    return groups



#Creates a histogram based on the scores and saves it to outPath.
def saveHistogram(scores, title, outPath, bins=20):
    df = pd.DataFrame({title: scores})
    hist = df.hist(bins=bins)
    fig = hist[0][0].get_figure()
    fig.savefig(outPath + "/" + title + ".png") 




def plotReadHists(groupData, outPath, bins=20):
   scores = {}
   for group in groupData:
       for row in groupData[group]:
            measure = row.measure
            if not measure in scores:
                scores[measure] = []

            scores[measure].append(row.score)
            
       for measure in scores:
            saveHistogram(scores[measure], measure + " - " + group, outPath, bins)




def plotCohHists(groupData, outPath, bins=20):
    scores = []
    for group in groupData:
        for row in group:
            scores.append(row.score)
        
        saveHistogram(scores, "LDA - " + group, outPath, bins)





parser = argparse.ArgumentParser()
parser.add_argument(
    'read_results',
    help='path to the tsv file containing the readability scores output',
    default=relative_file('../results/pmc_articles.all_readability_scores.csv'),
    nargs='?'
)
parser.add_argument(
    "coh_results",
    help='path to the tsv file containing the readability scores output',
    default=relative_file('../results/lda.results.tsv'),
    nargs='?'
)
parser.add_argument(
    "--outpath",
    help='output location for plots',
    default=relative_file("../results/plots"),
    nargs='?'
)
parser.add_argument(
    "--pmid_mappings",
    help='output location for plots',
    default=relative_file("../data/pmc_metadata.affiliations.countries.csv"),
    nargs='?'
)

parser.add_argument(
    "--max_rows",
    help='output location for plots',
    default="5000000",
    nargs='?'
)


args = parser.parse_args()

os.makedirs(args.outpath, exist_ok=True)

dfReadability = pd.read_csv(args.read_results)    #Read in readability tsv.
#dfCoherence = pd.read_csv(args.coh_results)      #Read in lda tsv.
pmidMappings = pd.read_csv(args.pmid_mappings)

print("Splitting readability data...")
readabilityGroups = splitGroups(dfReadability, pmidMappings, args.max_rows)

#print("Splitting coherence data...")
#ldaGroups = splitGroups(dfCoherence, pmidMappings, args.max_rows)

print("Plotting readability data...")
plotReadHists(readabilityGroups, args.outpath)

#print("Plotting coherence data...")
#plotCohHists(ldaGroups, args.outpath)







