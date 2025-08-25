#!/usr/bin/env python3.9

import os
import subprocess
import logging

from boto3 import client as boto3_client

logger = logging.getLogger('ResourcesManager')

def main():
    # Setup logging
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    sts_client = boto3_client("sts")

    logger.info("start of processing")

    resources = os.environ['RESOURCES_DIR'] # static resources
    node_identifier = os.environ['NODE_IDENTIFIER']
    env = os.getenv('ENVIRONMENT', 'local').lower()

    sync_resources(sts_client, env, node_identifier, resources)
    logger.info("end of processing")

def sync_resources(sts_client, env, node_identifier, resources_directory):
    if env == "local":
        logger.info("local environment detected, skipping s3 sync")
        return

    account_id = sts_client.get_caller_identity()["Account"]
    bucket_name = "tfstate-{0}".format(account_id)
    prefix = "{0}/{1}/resources".format(env, node_identifier)

    try:
        process = subprocess.Popen(
            ["aws", "s3", "sync", "s3://{0}/{1}/".format(bucket_name, prefix), resources_directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end="")  # real-time streaming
        process.wait()
    except process.CalledProcessError as e:
        logger.info(f"command failed with return code {e.returncode}")



if __name__ == '__main__':
    main()    