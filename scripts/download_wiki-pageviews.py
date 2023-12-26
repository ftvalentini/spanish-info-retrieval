"""Download pageviews from Wikipedia API using mwviews library.
"""

import argparse
import logging
from pathlib import Path

import datasets
import pandas as pd
from tqdm import tqdm
from mwviews.api import PageviewsClient


logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter(
    "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    "%m/%d/%Y %H:%M:%S",
)
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)


def main():

    # args:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfile", type=str, default="TODO")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--start_date", type=str, default="20160101", help="YYYYMMDD")
    parser.add_argument("--end_date", type=str, default="20211231", help="YYYYMMDD")
    args = parser.parse_args()

    # Check if outfile exists:
    if Path(args.outfile).exists() and not args.overwrite:
        logger.info(f"Outfile {args.outfile} already exists. "
                    "Exiting. Use --overwrite to overwrite.")
        return

    logger.info("Loading wikipedia documents...")
    # NOTE currently from miracl, maybe use ours with wikiextractor.
    # NOTE This downloads the corpus from HF even if we are pointing to a local 
    # folder because of the way data/miracl-corpus/miracl-corpus.py is written
    # TODO add param to specify local folder?
    miracl_corpus = datasets.load_dataset("data/miracl-corpus", "es")
    df_docs = miracl_corpus["train"].to_pandas()
    titles = df_docs["title"].unique().tolist()
    logger.info(f"Loaded {len(titles)} unique articles.")
    del miracl_corpus

    logger.info(f"Saving pageviews to {args.outfile}...")
    p = PageviewsClient(user_agent="Spanish Wikipedia analysis")
    chunk_size = 1200

    for i in tqdm(range(0, len(titles), chunk_size)):
        chunk_titles = titles[i : i + chunk_size]
        # NOTE in titles, space equals underscore :)
        res = p.article_views(
            "es.wikipedia",
            chunk_titles, 
            granularity="monthly",
            start=args.start_date,
            end=args.end_date,
        )
        # sum views across months (int):
        views_dict = pd.DataFrame(res).sum(axis=1).astype(int).to_dict()
        
        # append to outfile:
        with open(args.outfile, "a") as f:
            for title, views in views_dict.items():
                f.write(f"{title}\t{views}\n")

    logger.info("Done.")


if __name__ == "__main__":
    main()
