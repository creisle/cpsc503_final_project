mkdir -p data/pubmed
cd data/pubmed
wget https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz
gunzip PMC-ids.csv.gz
cd ../..
