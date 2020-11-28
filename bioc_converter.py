import bconv
import os
import regex

basePath = "data/pmc_small_sample"
outPath = "data/pmc_txt"
outFormat = "txt"
abstractPattern = ("(\r\n|\r|\n)(Abstract|ABSTRACT)((\r\n|\r|\n)(\r\n|\r|\n).+)+"
                   "((\r\n|\r|\n)(\r\n|\r|\n)(Introduction|INTRODUCTION))(\r\n|\r|\n)")
introPattern = ("(\r\n|\r|\n)(Introduction|INTRODUCTION)((\r\n|\r|\n)(\r\n|\r|\n).+)+" 
"((\r\n|\r|\n)(\r\n|\r|\n)(METHODS|Methods|Materials and methods|MATERIALS AND METHODS))(\r\n|\r|\n)")
discussionPattern = ("(\r\n|\r|\n)(Discussion|DISCUSSION)((\r\n|\r|\n)(\r\n|\r|\n).+)+" 
"((\r\n|\r|\n)(\r\n|\r|\n)(Conclusion|CONCLUSION)(s|S)?)(\r\n|\r|\n)")
text = ""
preProcessFailed = False


#Iterate over all dirs in the base path here and for each folder convert the contents
print("Converting bioc to " + outFormat + "...")
collections = os.listdir(basePath)
for c in collections:
    cPath = basePath + "/" + c
    papers = os.listdir(cPath)
    
    for pFile in papers:
        
        pPath = cPath + "/" + pFile
        curPaper = bconv.load(pPath, fmt='nxml', mode="collection")
        bconv.dump(curPaper, outPath, outFormat)
        

        try:
            print("Preprocessing " + pFile)
            preprocessFailed = False

            abstract = ""
            intro = ""
            discussion = ""
            pContents = ""
            
            with open(outPath + "/" + os.path.splitext(pFile)[0] + "." + outFormat, 'r+', encoding='utf-8') as outFile:
                pContents = outFile.read()
                abstractMatch = regex.search(abstractPattern, pContents, regex.MULTILINE)

                #Handle abstract section
                if (abstractMatch):
                    abstract = abstractMatch.group(0)
                    abstract = regex.sub("(\r\n|\r|\n)(Introduction|INTRODUCTION)(\r\n|\r|\n)", 
                    "", abstract)                                                                    #Remove the Introduction section header

                #Handle intro section
                introMatch = regex.search(introPattern, pContents, regex.MULTILINE)
                if(introMatch):
                    intro = introMatch.group(0)
                    intro = regex.sub("(\r\n|\r|\n)(METHODS|Methods|Materials and methods|MATERIALS AND METHODS)(\r\n|\r|\n)", 
                    "", intro)                                                                        #Remove the Methods section header

                #Handle discussion section
                discussionMatch = regex.search(discussionPattern, pContents, regex.MULTILINE)
                if(discussionMatch):
                    discussion = discussionMatch.group(0)
                    discussion = regex.sub("(\r\n|\r|\n)(Conclusion|CONCLUSION)(s|S)?(\r\n|\r|\n)", 
                        "", discussion)    

                text = abstract + "\n\n" + intro + "\n\n" + discussion

                text = regex.sub("(\s*\(\d+(,\s*\d+\s*)*\)|\[(\d+(,\s*\d+\s*)*\])\s*)", "", text)     #Remove numeric references

                outFile.seek(0)
                outFile.write(text)
                outFile.truncate()

        
        except:
                print("Preprocessing failed for " +pFile)
                preProcessFailed = True

        

    

print("Finished converting to txt. Output in " + outPath)