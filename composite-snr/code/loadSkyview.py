#!/usr/bin/env python


# 现在有一个很离谱的bug, 当传入坐标中包含:或者的时候，就会把两个坐标理解为一个参数
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.skyview import SkyView
import sys
import pandas as pd
import numpy as np
from argparse import ArgumentParser
from transCoord import trans_deg2hms
from mylogger import Logger
global logger
logger = Logger("skyload", 'test.txt')

def load_from_Skyview(coord1, coord2, coordinates, r_in, Survey_list, outDir=".", max_retries=5):
    """
    Load FITS images from SkyView with error handling and retry mechanism.

    Parameters:
    coord1 (str): First coordinate (RA or l).
    coord2 (str): Second coordinate (Dec or b).
    coordinates (str): Coordinate system, either "J2000" or "Galactic".
    r_in (float): Radius of the image in degrees.
    Survey_list (str): Path to the survey list text file.
    outDir (str): Output directory. Default is the current directory.
    max_retries (int): Maximum number of retries for failed surveys.
    """
    # Transform and log coordinates
    if "J" in coordinates.upper() or "FK5" in coordinates.upper():
        coord1_fk5hms, coord2_fk5hms = trans_deg2hms(coord1, coord2)
        coord1_fk5hms_name = coord1_fk5hms.replace(":", "").replace(" ", "").replace("h", "")[:4]
        coord2_fk5hms_name = "{:+.0f}".format(float(coord2_fk5hms.replace(":", "").replace(" ", "").replace("d", "")))[:3]
        name = f'J{coord1_fk5hms_name}{coord2_fk5hms_name}'
        logger.info(f'Input coordinates in J2000 (hms) are {coord1_fk5hms}, {coord2_fk5hms}')
    elif "G" in coordinates.upper():
        coord1_galdeg_name = "{:.1f}".format(float(coord1))
        coord2_galdeg_name = "{:+.1f}".format(float(coord2))
        name = f"G{coord1_galdeg_name}{coord2_galdeg_name}"
        logger.info(f'Input coordinates in Galactic (deg) are {coord1}, {coord2}')
    else:
        logger.error('Please provide the correct coordinates. We only accept "J2000" or "Galactic".')
        return

    r_in_deg = r_in * u.deg
    if r_in > 4:
        logger.warning('The size of the FITS file will be larger than 8 degrees.')

    try:
        coord1 = coord1_fk5hms
        coord2 = coord2_fk5hms
    except NameError:
        pass

    with open(Survey_list) as f:
        surveys = [line.strip() for line in f]

    failed_surveys = surveys.copy()
    retry_count = 0

    while failed_surveys and retry_count < max_retries:
        logger.info(f"Retry attempt {retry_count + 1}/{max_retries}")
        current_failures = []

        for survey in failed_surveys:
            position = f'{coord1}, {coord2}'
            logger.info(f'Downloading FITS file from {survey}. Center: {position}; radius: {r_in_deg}')
            pixels = int(r_in * 500)

            try:
                image = SkyView.get_images(position=position, coordinates=coordinates, survey=survey, radius=r_in_deg, pixels=pixels, projection="Sin")
                if not image:
                    raise ValueError(f"No data available for {survey} at {position} (r = {r_in_deg})")
            except Exception as e:
                logger.error(f"Error occurred for {survey}: {e}")
                current_failures.append(survey)
            else:
                outname = f"{name}_{r_in}_{survey.replace(' ', '-').replace('(', '').replace(')', '').replace('/', '-')}.fits"
                outFile = f'{outDir}/{outname}'
                logger.info(f'The loaded file will be saved in {outFile}')

                hdul = image[0]
                data = np.array(hdul[0].data, dtype=float, copy=True)
                data[np.isnan(data)] = 0.0

                zero_percentage = np.mean(data == 0.0) * 100
                if zero_percentage > 95:
                    logger.warning("More than 95% of data is 0.0. Skipping this survey.")
                else:
                    hdul.writeto(outFile, overwrite=True)

        failed_surveys = current_failures
        retry_count += 1

    if failed_surveys:
        logger.error(f"Failed to download data for the following surveys after {max_retries} retries: {failed_surveys}")
    else:
        logger.info("All surveys successfully downloaded.")


def get_args():
    _description = "Load FITS images from SkyView."
    ps = ArgumentParser(description=_description)
    ps.add_argument("coord1", type=str, help="RA or l")
    ps.add_argument("coord2", type=str, help="Dec or b")
    ps.add_argument("coordinates", type=str, help='Coordinate system, either "J2000" or "Galactic".')
    ps.add_argument('r_in', type=float, help='Radius of the image in degrees.')
    ps.add_argument('Survey_list', type=str, default='./skyviewList/test.txt',help='Path to the survey list text file.')
    ps.add_argument('-o', '--outDir', type=str, default='.', help='Output directory. Default is the current directory.')
    args = ps.parse_args()
    logger.info(args)
    return args

def cli():


    args = get_args()
    arg_dict = vars(args)
    logger.info(arg_dict)
    load_from_Skyview(**arg_dict)
    # load_from_Skyview(
    #     coord1=args.coord1, 
    #     coord2=args.coord2,
    #     coordinates=args.coordinates, 
    #     r_in=args.r_in, 
    #     Survey_list=args.Survey_list,
    #     outDir=args.outDir)

if __name__ == "__main__":
    cli()
