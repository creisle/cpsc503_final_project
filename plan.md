Conversion notes:

* Docs to Markdown version 1.0β29
* Mon Oct 26 2020 14:56:49 GMT-0700 (PDT)
* Source doc: CPSC503 - Final Project Ideas
----->



## Deadlines/Dates



*   Meeting with giuseppe: Oct 19th 3pm
*   Initial Proposal: Nov 4th?


## Work Plan


### Initial



*   [/] set up repo
*   download data (each do some locally, i will try to get all on work/school server)
*   initial analysis: grams to evaluate similarity (k-means?)
*   scoring of articles (1 from each journal?) depending on the number of journals using traditional readability scoring (for later comparisons)
*   ??? 


### Putative Extensions



*   concept extraction/identification (way to measure the amount of background knowledge required for a reading)? for scientific articles this would contribute heavily to actual ‘readability’
*   score/classify reading-level based on the users expertise or previous readings? 


## Ideas



1. Classifying scientific articles by readability (check this has been done on literature since there are “readability” lists that can verify those on)
2. classifying/clustering scientific articles based on specialized vernacular
    1. maybe decompose them all into grams/phrases (could be more sophisticated about splitting into phrases instead of grams if we use POS to determine where to split?) 
    2. then remove any grams/phrases that occur in  all of them or some threshold?
    3. recommender? 
    4. common phrases need to know when starting a new field
3. predict the journal an article belongs to? similar to clustering based on topic


## Corpus / Data



*   Data can be retrieved from here: [https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/](https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/) 
*   grammarly coherence dataset: 
    *   [[1805.04993] Discourse Coherence in the Wild: A Dataset, Evaluation and Methods](https://arxiv.org/abs/1805.04993) 
    *   [aylai/GCDC-corpus: Grammarly Corpus of Discourse Coherence and accompanying code for discourse coherence models](https://github.com/aylai/GCDC-corpus) 


## Possibly Relevant Background 

Note: just collecting things that look relevant, haven’t read them all in detail



*   [Readability Assessment of Online Patient Education Material on Congestive Heart Failure](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5471568/) (2017)
*   [Readability in the British Journal of Surgery](https://pubmed.ncbi.nlm.nih.gov/18076017/) (2008)
*   [Assessing reading levels of health information: uses and limitations of flesch formula](https://pubmed.ncbi.nlm.nih.gov/28707643/) (2017)
*   [A Machine Learning Approach to Reading Level Assessment](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.105.8671&rep=rep1&type=pdf) (2006)
*   [Moving beyond classic readability formulas: new methods and new models](https://onlinelibrary.wiley.com/doi/abs/10.1111/1467-9817.12283) (2019)
*   [The readability of scientific texts is decreasing over time](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5584989/) (2017)
*   McNamara
    *   [Applying Natural Language Processing and Hierarchical Machine Learning Approaches to Text Difficulty Classification](https://link-springer-com.ezproxy.library.ubc.ca/article/10.1007/s40593-020-00201-7) (2020)
    *   [Assessing Text Readability Using Cognitively Based Indices - CROSSLEY - 2008 - TESOL Quarterly](https://onlinelibrary.wiley.com/doi/abs/10.1002/j.1545-7249.2008.tb00142.x) (2011)
*   [Neural RST-based Evaluation of Discourse Coherence](https://arxiv.org/abs/2009.14463) (2020 | prev year project)
*   [Revisiting Readability: A Unified Framework for Predicting Text Quality](https://www.aclweb.org/anthology/D08-1020/) (2008)
*   [A Neural Local Coherence Model for Text Quality Assessment](https://www.aclweb.org/anthology/D18-1464/) (2018) 
*   [Gondy Leroy](https://www.ncbi.nlm.nih.gov/pubmed/?term=Leroy%20G%5BAuthor%5D&cauthor=true&cauthor_uid=24100710)
    *   [The effect of word familiarity on actual and perceived text difficulty](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3957403/) (2014)
    *   [Measuring Text Difficulty Using Parse-Tree Frequency](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5644354/) (2018)
    *   [Using Lexical Chains to Identify Text Difficulty: A Corpus Statistics and Classification Study](https://pubmed.ncbi.nlm.nih.gov/30530380/) (2018)
    *   [Moving Beyond Readability Metrics for Health-Related Text Simplification](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5044755/) (2016) 
*   [Readability Formulas and User Perceptions of Electronic Health Records Difficulty: A Corpus Study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5355629/) (2017) 
*   concept extraction
    *   [Unsupervised concept extraction from clinical text through semantic composition](https://www.sciencedirect.com/science/article/pii/S1532046419300383) (2019) 


## Common Readability Scores/Tests



*   [Flesch–Kincaid readability tests](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
    *   Tends to inappropriately distinguish very sharply between low and high cohesion texts
*   [Gunning fog index](https://en.wikipedia.org/wiki/Gunning_fog_index) 
*   [SMOG](https://en.wikipedia.org/wiki/SMOG)
*   [Coleman–Liau index](https://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index)


## Baseline



*   [TAACO](https://www.linguisticanalysistools.org/taaco.html)
    *   [The Tool for the Automatic Analysis of Cohesion 2.0: Integrating semantic similarity and text overlap](https://link.springer.com/article/10.3758/s13428-018-1142-4) (2019) 
    *   pre-implemented


## Useful Tools

Weka: [https://www.cs.waikato.ac.nz/ml/weka/](https://www.cs.waikato.ac.nz/ml/weka/) 

readability metrics: [https://pypi.org/project/textstat/](https://pypi.org/project/textstat/) 

Another readability metrics package: [Text-classification-into-difficulty-stores](https://github.com/madhurimamandal/Text-classification-into-difficulty-levels)   (not as good)


## First Steps



*   for all of these ideas we should download PMC full text articles (might be able to do this off just abstracts if we want to)
    *   this will take a lot of space, i have to do this for my own work anyway so I will be able to requisition space, just not sure about being able to share access which could be problematic
*   score some articles to show the low readability hypothesis of scientific articles is correct
    *   compare review vs primary research article


## Introduction/Motivation

Most work on readability or measuring text difficulty has focused on accessibility to the general population which assumes a low reading level (ADD REF). However an analogous problem exists within research itself. As the domain of knowledge increases, so does the burden on the researchers. Increasingly scientific literature requires domain-specific knowledge and vernacular which is a barrier to entry ([PMC5584989](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5584989/)). The long term goal of this project is a recommender system for researchers that will optimize learning a new field by recommending papers that match the researchers knowledge level in the field. This will involve the assessment of readability, coherence, and knowledge (concept) requirements of scientific literature. 


#### Aim 1: Measure the effectiveness of traditional readability scoring systems on scientific literature. 

_<span style="text-decoration:underline;">Hypothesis</span>_: Scoring will result in a high reading level for most scientific literature and will not effectively separate articles.

Most readability scores depend heavily on word and sentence length which are not always a good measure of simplicity, particularly in scientific or health-related literature ([PMC5644354](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5644354/)). We will apply the traditional scoring to a subset of the articles available from pubmed central full text articles open data set.

Aim. Compare/Apply methods for Cohesion/Coherence on our dataset



*   pick the methods that are “state of the art” and “doable”
*   apply and see if they satisfy dataset or just all classified the same
*   look into individual examples

Aim 2. Compute Concept Similarity????

_<span style="text-decoration:underline;">Hypothesis</span>_: Articles from similar fields will share more specialized vernacular / concepts. 



*   complex: identify abstract concepts and compare
*   simple: compare grams (2-5)? remove anything that is universal or highly prevalent. perhaps look at which ones can be used to stratify articles into their journals (proxy for topic)
*   keywords on article might be able to be used as a ground-truth metric. tho they are hardly exhaustive

Aim X. Neural classifier to distinguish review vs non-review articles? 



*   have a good ground truth
*   using review as proxy for more readability
*   might be overly influenced by article length, would need to use that as a baseline

Aim 3. Design of a system of collection of a ground-truth set of data for the reading of scientific articles 
