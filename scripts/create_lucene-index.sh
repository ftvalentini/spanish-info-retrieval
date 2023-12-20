#!/bin/bash -e

mkdir -p logs

lang="es"

corpus_dir="data/miracl-corpus/miracl-corpus-v1.0-${lang}"
out_dir="runs/indexes/lucene-index.miracl-v1.0-${lang}"

python -m pyserini.index.lucene --collection MrTyDiCollection \
  --input $corpus_dir \
  --index $out_dir \
  --generator DefaultLuceneDocumentGenerator \
  --threads 12 --storePositions --storeDocvectors \
  --storeRaw -language ${lang} \
  >& logs/log.miracl-v1.0-${lang} &



