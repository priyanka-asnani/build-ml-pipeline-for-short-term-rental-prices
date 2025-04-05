#!/usr/bin/env python
"""
performs basic cleaning of the data and saves the results in W&B
"""
import argparse
import logging
import wandb
import datetime
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading artifact {args.input_artifact}")

    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()
    
    logger.info(f"Started pre-processing")
    df = pd.read_csv(artifact_path)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info(f"Uploading {args.artifact_name} to Weights & Biases")

    filename = "processed_data.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        name=args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")

    parser.add_argument("input_artifact", type=str)
    parser.add_argument("artifact_name", type=str)
    parser.add_argument("artifact_type", type=str)
    parser.add_argument("artifact_description", type=str)
    parser.add_argument("--min_price", type=int, required=True)
    parser.add_argument("--max_price", type=int, required=True)

    args = parser.parse_args()
    go(args)

