#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import numpy as np


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# DO NOT MODIFY
def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    
    run = wandb.init(project="nyc_airbnb", group="cleaning", save_code=True)
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])



    # ✅ Drop NaNs in longitude and latitude BEFORE filtering
    df = df.dropna(subset=['longitude', 'latitude'])

    # ✅ Before boundary filtering
    print(f"🚀 Before filtering: {df.shape[0]} rows")

    # ✅ Apply boundary filtering for NYC
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()  # This should remove out-of-bound rows

    # ✅ After boundary filtering
    print(f"✅ After filtering: {df.shape[0]} rows")

    # ✅ Print data types of longitude and latitude before running the boundary test
    print("\n📊 Checking data types before boundary test:")
    print(df[['longitude', 'latitude']].dtypes) 

    def test_proper_boundaries(data: pd.DataFrame):
        """
        Test proper longitude and latitude boundaries for properties in and around NYC.
        If failing rows exist, print them for debugging.
        """
        print("\n🚀 Checking property boundaries...")

        # Create boolean mask for rows within the valid range
        idx = data['longitude'].between(-74.25, -73.50) & data['latitude'].between(40.5, 41.2)

        # Find failing rows (out-of-bounds properties)
        failing_rows = data[~idx]

        if not failing_rows.empty:
            print("\n🚨🚨🚨 Failing Rows 🚨🚨🚨")
            print(failing_rows[['id', 'longitude', 'latitude']])  # Print only relevant columns
            print(f"\n🚨 Total failing rows: {len(failing_rows)}")

            # Save the failing rows to a CSV for manual inspection
            failing_rows.to_csv("failing_rows.csv", index=False)
            print("\n📂 Saved failing rows to 'failing_rows.csv' for debugging.")

    # Assert to fail if any out-of-bounds rows exist
    assert np.sum(~idx) == 0, "❌ There are still out-of-bounds rows after filtering!"

    # ✅ Print data types of longitude and latitude before running the boundary test
    print("\n📊 Checking data types before boundary test:")
    print(df[['longitude', 'latitude']].dtypes)

    # ✅ Print min/max values to confirm dataset range
    print("\n📌 Min/Max Values Before Filtering:")
    print(f"Longitude: min={df['longitude'].min()}, max={df['longitude'].max()}")
    print(f"Latitude: min={df['latitude'].min()}, max={df['latitude'].max()}")

    # ✅ Print count of NaNs before filtering
    print("\n🛑 Checking for NaN values before filtering:")
    print(df[['longitude', 'latitude']].isna().sum())

    # ✅ Print after filtering
    print("\n✅ After filtering:")
    print(f"Remaining rows: {df.shape[0]}")
    print(f"Longitude: min={df['longitude'].min()}, max={df['longitude'].max()}")
    print(f"Latitude: min={df['latitude'].min()}, max={df['latitude'].max()}")

    # ✅ Run boundary test
    test_proper_boundaries(df)


    # ✅ Run boundary test to make sure filtering worked
    test_proper_boundaries(df)

    # Save the cleaned file
    df.to_csv('clean_sample.csv',index=False)

    # log the new data.
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
 )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


# TODO: In the code below, fill in the data type for each argumemt. The data type should be str, float or int. 
# TODO: In the code below, fill in a description for each argument. The description should be a string.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")
  
    parser.add_argument(
        "--input_artifact", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Ininital artifact to be cleaned", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--output_artifact", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Output artifact for cleaned data", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--output_type", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Type of the output dataset", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--output_description", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Description of the output dataset", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--min_price", 
        type = float, ## INSERT TYPE HERE: str, float or int,
        help = "Minimum house price to be considered", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--max_price",
        type = float, ## INSERT TYPE HERE: str, float or int,
        help = "Maximum house price to be considered", ## INSERT DESCRIPTION HERE,
        required = True
    )


    args = parser.parse_args()

    go(args)