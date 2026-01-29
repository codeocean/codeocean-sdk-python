import os

from codeocean import CodeOcean
from codeocean.models.computation import RunParams
from codeocean.models.data_asset import DataAssetParams, Source, ComputationSource


# Create the client using your domain and API token.

client = CodeOcean(domain=os.environ["CODEOCEAN_URL"], token=os.environ["API_TOKEN"])

# Get capsule.

capsule = client.capsules.get_capsule(capsule_id=os.environ["CAPSULE_ID"])

# Run a capsule.

run_params = RunParams(capsule_id=capsule.id)

computation = client.computations.run_capsule(run_params)

# Wait for computation to finish.

computation = client.computations.wait_until_completed(computation)

# Create a data asset from computation results.

data_asset_params = DataAssetParams(
    name="My Result",
    description="Computation result",
    mount="my-result",
    tags=["my", "result"],
    source=Source(
        computation=ComputationSource(
            id=computation.id,
        ),
    ),
)

data_asset = client.data_assets.create_data_asset(data_asset_params)

data_asset = client.data_assets.wait_until_ready(data_asset)
