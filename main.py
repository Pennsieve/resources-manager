#!/usr/bin/env python3.9

import os
import subprocess

from boto3 import client as boto3_client
from logger import ResourcesManagerLogger

def main():
    logger = ResourcesManagerLogger()
    sts_client = boto3_client("sts")

    print("start of processing")
    resources = os.environ['RESOURCES_DIR'] # static resources
    node_identifier = os.environ['NODE_IDENTIFIER']
    env = os.getenv('ENVIRONMENT', 'local').lower()

    sync_resources(sts_client, env, node_identifier, resources, logger)

def sync_resources(sts_client, env, node_identifier, resources_directory, logger):
    if env == "local":
        return

    account_id = sts_client.get_caller_identity()["Account"]
    bucket_name = "tfstate-{0}".format(account_id)
    prefix = "{0}/{1}/resources".format(env, node_identifier)

    try:
        output = subprocess.run(["aws", "s3", "sync", "s3://{0}/{1}/".format(bucket_name, prefix), resources_directory]) 
        logger.info(output)
    except subprocess.CalledProcessError as e:
        logger.info(f"command failed with return code {e.returncode}")

if __name__ == '__main__':
    main()    