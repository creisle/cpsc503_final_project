import bconv
import os

basePath = "data/pmc_small_sample"
outPath = "data/pmc_txt"
outFormat = "txt"

#Iterate over all dirs in the base path here and for each folder convert the contents
print("Converting bioc to " + outFormat + "...")
collections = os.listdir(basePath)
for c in collections:
    cPath = basePath + "/" + c
    papers = os.listdir(cPath)
    
    for pFile in papers:
        try:
            pPath = cPath + "/" + pFile
            curPaper = bconv.load(pPath, fmt='nxml', mode="collection")
            bconv.dump(curPaper, outPath, outFormat)
        except:
            print("Converting the file " + pPath + " failed.")


print("Finished converting to txt. Output in " + outPath)