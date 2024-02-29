import pandas as pd
from astroquery.simbad import Simbad
import os


## Utilities

def find_gaia_dr3(value: str):
    catalog = "Gaia DR3"
    if catalog in value:
        index = value.index(catalog)
        return value[index + len(catalog) + 1:index + len(catalog) + 25].strip().split('|')[0].strip()
    else:
        return None


def generate_queries(main_type):
    template = "maintype='{main_type}' & rah >= {left}  & rah < {right}"
    return [template.format(main_type=main_type, left=i, right=i + 1) for i in list(range(25))]


simbad_handler = Simbad()
simbad_handler.ROW_LIMIT = 0
simbad_handler.TIMEOUT = 60 * 60
simbad_handler.reset_votable_fields()

simbad_handler.add_votable_fields(
    "otype",
    "typed_id",
    "id(Gaia)",
    "ids",
    "sptype",
    "otypes"
)


def download_data(queries, out_name: str):
    out_dir = 'symbad'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    fullname = os.path.join(out_dir, out_name)

    result = []
    for query in queries:
        result_table = simbad_handler.query_criteria(query)
        df1 = result_table.to_pandas()
        print(df1.shape)
        df_result = df1[['MAIN_ID', 'OTYPE', 'SP_TYPE', 'ID_Gaia', 'IDS', 'OTYPES']]
        df_result['Gaia DR3'] = df_result.apply(lambda row: find_gaia_dr3(row['IDS']), axis=1)
        # df_result['Gaia DR3'] = df_result['IDS'].apply(find_gaia_dr3)
        df_result = df_result.dropna(subset=['Gaia DR3'])
        print(df_result.shape)
        result.append(df_result)

    combined_pd = pd.concat(result)
    combined_pd.to_csv(fullname, header=True, index=False)


## Download Symbiotic Stars (Symbad)
queries = generate_queries('Sy*')
out_name = 'SY.csv'
download_data(queries, out_name)

## Download Planetary Nebula (Symbad)
queries = generate_queries('PN')
out_name = 'PN.csv'
download_data(queries, out_name)

## Download Be stars (Symbad)
queries = generate_queries('Be*')
out_name = 'Be.csv'
download_data(queries, out_name)

## Download Cataclysmic Variables (CV) (Symbad)
queries = generate_queries('CV*')
out_name = 'CV.csv'
download_data(queries, out_name)

## Download Mira (Symbad)
queries = generate_queries('Mi*')
out_name = 'Mira.csv'
download_data(queries, out_name)

## Download AeBe stars (Symbad)
queries = generate_queries('Ae*')
out_name = 'Ae.csv'
download_data(queries, out_name)

## Download AeBe stars (Symbad)
queries = generate_queries('Ae*')
out_name = 'Ae.csv'
download_data(queries, out_name)

## Download Young stellar objects (Symbad)
queries = generate_queries('Y*O')
out_name = 'YSO.csv'
download_data(queries, out_name)

## Download Wolf-Rayet stars (Symbad)
queries = generate_queries('WR*')
out_name = 'WR.csv'
download_data(queries, out_name)

## post-AGB stars (Symbad)
queries = generate_queries('pA*')
out_name = 'pAGB.csv'
download_data(queries, out_name)

## Download weak/classical T Tauri stars (WTT/ClTT) (Symbad)
queries = generate_queries('TT*')
out_name = 'TT.csv'
download_data(queries, out_name)
