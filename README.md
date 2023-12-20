
## Set up

Create conda environment:

```bash
conda create -n spanish-ir python=3.10
```

And install requirements:

```bash
conda activate spanish-irtm
# # For GPU, install pytorch with the correct cuda version (see output of nvidia-smi):
# conda install pytorch pytorch-cuda=11.7 -c pytorch -c nvidia
# For CPU only:
conda install pytorch cpuonly -c pytorch
# Install jdk (needed for pyserini)
conda install -c conda-forge openjdk=11 maven -y
pip install -r requirements.txt
```

Install git lfs to git clone large files from huggingface:

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash &&
sudo apt-get install git-lfs &&
git lfs install
```

Others:

```bash
chmod +x scripts/*.sh
```

**Note**: you might have issues installing `nmslib`. If so, do the following:

```bash
pip install --upgrade pybind11        # 2.10.1 or higher  (latest as of today: 2.11.1)
pip install --verbose  'nmslib @ git+https://github.com/nmslib/nmslib.git#egg=nmslib&subdirectory=python_bindings'
```

Then, re-run `pip install -r requirements.txt`. See [this](https://github.com/nmslib/nmslib/issues/538) for further details.

### Verify pyserini installation

Verify BM25 retrieval works on prebuilt index on NFC dataset:

```bash
python -m pyserini.search.lucene \
    --index beir-v1.0.0-nfcorpus.flat \
    --topics beir-v1.0.0-nfcorpus-test \
    --output tmp_run.beir-v1.0.0-nfcorpus-flat.trec \
    --output-format trec \
    --batch 36 --threads 12 \
    --remove-query --hits 1000

python -m pyserini.eval.trec_eval -c -m ndcg_cut.10 -m recall.100,1000 beir-v1.0.0-nfcorpus-test tmp_run.beir-v1.0.0-nfcorpus-flat.trec
```

Verify dense retrieval with contriever on prebuilt index on NFC dataset:

```bash
python -m pyserini.search.faiss \
    --encoder-class contriever --encoder facebook/contriever-msmarco \
    --index beir-v1.0.0-nfcorpus.contriever \
    --topics beir-v1.0.0-nfcorpus-test \
    --output tmp_run.beir.contriever-msmarco.nfcorpus.txt \
    --batch 128 --threads 16 \
    --remove-query --hits 1000

python -m pyserini.eval.trec_eval -c -m ndcg_cut.10 -m recall.100,1000 beir-v1.0.0-nfcorpus-test tmp_run.beir.contriever-msmarco.nfcorpus.txt
```

Sources:

* https://github.com/castorini/pyserini/blob/e6700f6a1bca7d2bea81fb40d9c3ae63c1be142a/docs/installation.md?plain=1#L75
* https://github.com/castorini/pyserini/blob/e6700f6a1bca7d2bea81fb40d9c3ae63c1be142a/scripts/beir/run_beir_baselines.py#L57



### Create BM25 Lucene index


Download MIRACL documents, queries and qrels (all languages):

```bash
# Requires Access Token authentication:
mkdir -p data &&
cd data && 
git clone https://huggingface.co/datasets/miracl/miracl-corpus && 
git clone https://huggingface.co/datasets/miracl/miracl &&
cd -
```

Create index:

```bash
scripts/create_lucene-index.sh
```

Replicate results from Table 2 in https://arxiv.org/pdf/2210.09984.pdf:

```bash
# Run retrieval on dev set:
python -m pyserini.search.lucene  \
    --index  runs/indexes/lucene-index.miracl-v1.0-es \
    --topics data/miracl/miracl-v1.0-es/topics/topics.miracl-v1.0-es-dev.tsv \
    --output runs/run.miracl-v1.0-es.bm25.topics.miracl-v1.0-es.dev.txt \
    --bm25 --language es

# Evaluate with nDCG@10 & Recall@100:
python -m pyserini.eval.trec_eval -c -m ndcg_cut.10 -m recall.100  \
    data/miracl/miracl-v1.0-es/qrels/qrels.miracl-v1.0-es-dev.tsv \
    runs/run.miracl-v1.0-es.bm25.topics.miracl-v1.0-es.dev.txt
# recall_100              all     0.7018
# ndcg_cut_10             all     0.3193
```

Source: https://github.com/castorini/pyserini/blob/1219cdbca780e869ba77658c29e1aaa972585d09/docs/experiments-miracl-v1.0.md



--------------------

Training DPR with pyserini requires a Lucene index to retrieve negatives with BM25. To build the index, use:

* https://github.com/castorini/pyserini/blob/1219cdbca780e869ba77658c29e1aaa972585d09/docs/experiments-miracl-v1.0.md#1-manual-download


To train DPR with pyserini:

* https://github.com/castorini/pyserini/blob/1219cdbca780e869ba77658c29e1aaa972585d09/pyserini/resources/index-metadata/faiss.miracl-v1.0.mdpr-tied-pft-msmarco-ft-miracl.20230329.e40d4a.README.md#miracl-v10-mdpr-tied-pft-msmarco-ft-miracl-lang

Training requires tevatron.



