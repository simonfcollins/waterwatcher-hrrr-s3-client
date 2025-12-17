from datetime import datetime, timedelta, timezone
from fetch_hrrr import fetch_zarr, autoremove_zarrs
import os
import s3fs

fs = s3fs.S3FileSystem(anon=True)
grid_path = "/data/hrrrzarr/conus/grid"
os.makedirs(grid_path, exist_ok=True)

def main():
    file_list = os.listdir(grid_path)

    for f in ["HRRR_latlon.h5", "projparams.json"]:
        if f not in file_list:
            fs.get(f"s3://hrrrzarr/grid/{f}", f"{grid_path}/{f}")
            print(f"Downloaded {f}")

    utc_now = datetime.now(timezone.utc) - timedelta(hours=3)

    # fetch current forecast file
    fetch_zarr(utc_now.strftime("%Y%m%d"), utc_now.strftime("%H"), product_type="fcst")

    # fetch analysis files for last 12 hours
    for i in range(12):
        t = utc_now - timedelta(hours=i)
        fetch_zarr(t.strftime("%Y%m%d"), t.strftime("%H"), product_type="anl")

    # cleanup
    autoremove_zarrs()

    print("Exiting setup")

if __name__ == "__main__":
    main()