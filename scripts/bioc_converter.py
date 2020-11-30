import bconv
import os
import regex
import argparse




parser = argparse.ArgumentParser()
parser.add_argument(
    '--in_file', 
    help='the input bioc file',
    default="D:/pmc_archive"
)
parser.add_argument(
    '--out_file',
    help='the output txt file',
    default="D:/pmc_archive/pmc_txt"
)

args = parser.parse_args()

if not os.path.exists(args.in_file):
    raise FileNotFoundError(args.in_file)


inPath = args.in_file
outPath = args.out_file
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

       
paper = bconv.load(inPath, fmt='nxml', mode="collection")
bconv.dump(paper, outPath, outFormat)
       
try:
    print("Preprocessing " + inPath)
    preprocessFailed = False
    abstract = ""
    intro = ""
    discussion = ""
    pContents = ""
            
    with open(outPath, 'r+', encoding='utf-8') as outFile:
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