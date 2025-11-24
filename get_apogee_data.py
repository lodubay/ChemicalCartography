"""
This script downloads the APOGEE DR17 catalog and converts it to a CSV.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from astropy.table import Table

# Data file names
ALLSTAR_FNAME = 'allStarLite-dr17-synspec_rev1.fits'
DATA_DIR = 'data' # just keep data files in the root directory

def main():
    # Download DR17 allStar file from SDSS server
    print('Downloading allStar file (this will take a few minutes)...')
    url_write(
        'https://data.sdss.org/sas/dr17/apogee/spectro/aspcap/dr17/synspec_rev1/%s' \
        % ALLSTAR_FNAME, savedir=DATA_DIR)
    # Convert fits file to pandas DataFrame
    print('Importing allStar fits file...')
    apogee_catalog = fits_to_pandas(Path(DATA_DIR, ALLSTAR_FNAME), hdu=1)
    # Save to CSV
    print('Exporting to CSV...')
    apogee_catalog.to_csv(Path(DATA_DIR, 'APOGEEdata.csv'), index=False)
    print('Done!')


def fits_to_pandas(path, **kwargs):
    """
    Import a table in the form of a FITS file and convert it to a pandas
    DataFrame.

    Parameters
    ----------
    path : Path or str
        Path to fits file
    Other keyword arguments are passed to astropy.table.Table

    Returns
    -------
    df : pandas DataFrame
    """
    # Read FITS file into astropy table
    table = Table.read(path, format='fits', **kwargs)
    # Filter out multidimensional columns
    cols = [name for name in table.colnames if len(table[name].shape) <= 1]
    # Convert byte-strings to ordinary strings and convert to pandas
    df = decode(table[cols].to_pandas())
    return df


def decode(df):
    """
    Decode DataFrame with byte strings into ordinary strings.

    Parameters
    ----------
    df : pandas DataFrame
    """
    str_df = df.select_dtypes([object])
    str_df = str_df.stack().str.decode('utf-8').unstack()
    for col in str_df:
        df[col] = str_df[col]
    return df


def url_write(url, savedir='.'):
    """
    Retrieve a text file from the provided URL, decompressing if necessary.
    
    Parameters
    ----------
    url : str
        URL of text file to download.
    savedir : str or pathlib.Path, optional
        Directory to save the downloaded file. The default is '.'.
    """
    # These packages are only needed when building the sample from scratch.
    import gzip
    import urllib.request
    fname = url.split('/')[-1]
    with urllib.request.urlopen(url) as response:
        resp = response.read()
    # Decompress file if needed
    if fname[-3:] == '.gz':
        resp = gzip.decompress(resp)
        fname = fname[:-3]
    with open(Path(savedir) / fname, 'wb') as f:
        f.write(resp)


if __name__ == '__main__':
    main()
