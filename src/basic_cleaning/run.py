#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd



logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# DO NOT MODIFY
def go(args):

    # run = wandb.init(job_type="basic_cleaning")
    # run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    
    run = wandb.init(project="nyc_airbnb", group="cleaning", save_code=True)
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    ##### KIM: FIX - failing due to out-of-bounds data
    logger.info('Cleaning data.')

    # ✅ **Step 2: Convert last_review to datetime**
    df['last_review'] = pd.to_datetime(df['last_review'])

    # ✅ **Step 3: Filter properties outside NYC boundaries**
    boundary_filter = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.49, 41.2)

    # Check rows that are outside the boundary
    out_of_bounds = df[~boundary_filter]
    print(f"Total rows before boundary filter: {len(df)}")
    print(f"Rows outside boundary: {len(out_of_bounds)}")
    if not out_of_bounds.empty:
        print(out_of_bounds[['id', 'longitude', 'latitude']])

    # Apply the boundary filter to df
    df = df[boundary_filter].copy()

    # ✅ **Debugging: Print any out-of-bound rows**
    out_of_bounds = df[~boundary_filter]
    if not out_of_bounds.empty:
        logger.warning(f"❌ Found {len(out_of_bounds)} out-of-bounds listings:")
        print(out_of_bounds[['id', 'longitude', 'latitude']])  # Show affected listings

    # ✅ **Step 4: Apply the boundary filter**
    df = df[boundary_filter].copy()

    # # ✅ **Step 5: Save the cleaned file**
    # df.to_csv('clean_sample.csv', index=False)

    # # ✅ **Step 6: Log the cleaned data**
    # artifact = wandb.Artifact(
    #     args.output_artifact,
    #     type=args.output_type,
    #     description=args.output_description,
    # )
    # artifact.add_file("clean_sample.csv")
    # run.log_artifact(artifact)

    ##### KIM CODE ENDS #####


    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

#   # Convert last_review to datetime
#     df['last_review'] = pd.to_datetime(df['last_review'])

    # idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    # df = df[idx].copy()

    # # Allow latitude slightly below 40.5 (with a tolerance) 
    # idx = (df['longitude'].between(-74.25, -73.50)) & (df['latitude'].between(40.49, 41.2))  # Use 40.49 as a lower bound
    # df = df[idx].copy()
    
    # # https://knowledge.udacity.com/questions/1021000
    # logger.info('Cleaning data.')
    # idx = df['price'].between(float(args.min_price), float(args.max_price))
    # df = df[idx].copy()
    # df['last_review'] = pd.to_datetime(df['last_review'])

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