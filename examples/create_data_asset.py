import os

from codeocean import CodeOcean
from codeocean.data_asset import DataAssetParams, Source, AWSS3Source


# Create the client using your domain and API token.

client = CodeOcean(domain=os.environ["CODEOCEAN_URL"], token=os.environ["API_TOKEN"])

# Create a data asset from an S3 bucket.

data_asset_params = DataAssetParams(
    name="Dataset From Bucket",
    description="S3 bucket import",
    mount="my-data",
    tags=["my", "data"],
    source=Source(
        aws=AWSS3Source(
            bucket=os.environ["S3_BUCKET"],
            prefix=os.environ.get("S3_BUCKET_PREFIX"),
            public=os.environ.get("S3_BUCKET_PUBLIC", "").lower() in ["true", "1"],
        ),
    ),
)

data_asset = client.data_assets.create_data_asset(data_asset_params)

data_asset = client.data_assets.wait_until_ready(data_asset)
