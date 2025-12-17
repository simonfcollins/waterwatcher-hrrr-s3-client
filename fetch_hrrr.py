import s3fs
import os
import zarr
from datetime import datetime, timezone, timedelta
from shutil import rmtree

fs = s3fs.S3FileSystem(anon=True)
local_mslma_store_path = "/data/hrrrzarr/conus/sfc"
os.makedirs(local_mslma_store_path, exist_ok=True)


class BadArgumentException(Exception):
    pass


def download_zarr_group(rpath: str, lpath: str) -> None:
    """
    Downloads a zarr group from rpath to lpath.

    :param rpath: A path to a remote AWS S3 bucket.
    :param lpath: The path to save the zarr file to.
    :return: Void
    """
    remote_group = fs.get_mapper(rpath)
    local_store = zarr.DirectoryStore(lpath)
    zarr.copy_store(remote_group, local_store)


def fetch_zarr(date_str : str, cycle_str : str, product_type: str) -> None:
    """
    Fetches either a forecast or analysis zarr file from the specified date and cycle.

    :param date_str: The date to fetch from, as a string following the format 'YYYYMMDD'
    :param cycle_str: The hour to fetch from, as a string following the format 'HH' (24hr).
    :param product_type: 'fcst' | 'anl' - Specifies whether the zarr should contain forecast, or analysis data.
    :return: Void
    """
    if product_type not in ["anl", "fcst"]:
        raise BadArgumentException(f"Param 'product_type' must be either 'fcst' or 'anl', got '{product_type}'.")

    zarr_file_name = f"{date_str}_{cycle_str}z_{product_type}.zarr"
    rpath = f"s3://hrrrzarr/sfc/{date_str}/{zarr_file_name}/mean_sea_level"
    lpath = f"{local_mslma_store_path}/{zarr_file_name}/mean_sea_level"

    if os.path.exists(lpath):
        print(f"{lpath} already exists. Skipping.")
        return

    print(f"Fetching zarr group {rpath}...")
    download_zarr_group(rpath=rpath, lpath=lpath)
    print(f"Finished. Zarr group saved at {lpath}")


def autoremove_zarrs() -> None:
    """
    Removes all zarr files except the 12 most recent analysis files and the single most recent forecast file.

    :return: Void
    """
    print("Starting cleanup")
    files = os.listdir(local_mslma_store_path)

    anl_files = sorted([f for f in files if f.endswith("anl.zarr")])
    fcst_files = sorted([f for f in files if f.endswith("fcst.zarr")])

    # keep most recent forecast file
    if len(fcst_files) > 1:
        print(f"Removing old forecast files...")
        old = fcst_files[:-1]
        for f in old:
            full_path = os.path.join(local_mslma_store_path, f)
            if full_path.startswith(local_mslma_store_path):
                rmtree(full_path)
                print(full_path)
        print("Done")

    # keep last 12 analysis files
    if len(anl_files) > 12:
        print(f"Removing old analysis files...")
        old_anl = anl_files[:-12]
        for f in old_anl:
            full_path = os.path.join(local_mslma_store_path, f)
            if full_path.startswith(local_mslma_store_path):
                rmtree(full_path)
                print(full_path)
        print("Done")

    print("Cleanup finished")


def calc_date_cycle() -> tuple[str, str]:
    """
    Calculates date and cycle strings from current UTC time.


    :return: Up-to-date date and cycle strings.
    """
    utc_now = datetime.now(timezone.utc) - timedelta(hours=3)
    date_str = utc_now.strftime("%Y%m%d")
    cycle_str = utc_now.strftime("%H")
    return date_str, cycle_str


def update_prune_local_store() -> None:
    """
    Updates local zarr files and removes out-of-date ones.

    :return: Void
    """
    date_str, cycle_str = calc_date_cycle()
    fetch_zarr(date_str, cycle_str, 'anl')
    fetch_zarr(date_str, cycle_str, 'fcst')
    autoremove_zarrs()


def main():
    print("Syncing zarr stores...")
    update_prune_local_store()
    print("Sync complete")

if __name__ == "__main__":
    main()