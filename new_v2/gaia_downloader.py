import os
import zipfile
import pandas as pd
import numpy as np
from astroquery.gaia import Gaia
# Import the tool
from gaiaxpy import calibrate


## Utilities
def normalize(spectra):
    min1 = min(spectra)
    max1 = max(spectra)
    # Normalizar los espectros al rango de 0 a 1
    return (spectra - min1) / (max1 - min1)


def extract_zip(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall("./temp")


def download_from_gaia(file_name):
    df1 = pd.read_csv("./symbad/" + file_name)
    ids = df1['Gaia DR3'].astype(str).values

    out_dir = './gaia'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    index = 0
    i = 0
    # size = min(20000, len(ids))
    size = len(ids)
    df_result = []
    while index < size:
        elements = ids[index:index + 5000]
        fullname = os.path.join(out_dir, "XP_CONTINUOUS_COMBINED_{0}.zip".format(i))
        Gaia.load_data(
            ids=elements,
            format='csv',
            data_release='Gaia DR3',
            data_structure='COMBINED',
            retrieval_type='XP_CONTINUOUS',
            output_file=fullname,
            overwrite_output_file=True,
            verbose=True
        )

        i += 1
        print("finish", i)
        index += 5000

        extract_zip(fullname)
        df1 = pd.read_csv("./temp/XP_CONTINUOUS_COMBINED.csv")
        calibrated_spectra, sampling = calibrate(df1, save_file=False)
        df_result.append(calibrated_spectra)

    out_dir = './gaia_calibrated'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    result = pd.concat(df_result)
    result.to_csv(os.path.join(out_dir, file_name), header=True, index=False)

    # result['flux'] = result['flux'].apply(lambda x: np.array([float(j) for j in x.strip('[]').split()]))
    result['flux'] = result['flux'].apply(normalize)

    dfluxes = pd.DataFrame(result['flux'].tolist(), columns=range(343))

    out_dir = './normalized'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    fullname = os.path.join(out_dir, file_name)

    dfluxes.to_csv(fullname, header=False, index=False)
    print(dfluxes.shape[0])


# Download Sy
download_from_gaia("Ae.csv")
download_from_gaia("Be.csv")
download_from_gaia("CV.csv")
download_from_gaia("Mira.csv")
download_from_gaia("pAGB.csv")
download_from_gaia("PN.csv")
download_from_gaia("SY.csv")
download_from_gaia("TT.csv")
download_from_gaia("WR.csv")
download_from_gaia("YSO.csv")
