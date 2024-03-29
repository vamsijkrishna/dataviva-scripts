# -*- coding: utf-8 -*-
"""
    Example Usage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    python scripts/secex/format_raw_data.py \
    data/secex/raw_export/MDIC_2007.rar \
    data/secex/raw_import/MDIC_2007.rar \
    -y 2007 \
    -e data/comtrade/2007/comtrade_eci.tsv.bz2 \
    -p data/comtrade/2007/comtrade_pci.tsv.bz2 \
    -r data/comtrade/2007/comtrade_ypw.tsv.bz2 \
    -o data/secex/2007
"""

''' Import statements '''
import os, sys, time, bz2, click, MySQLdb
import pandas as pd
import pandas.io.sql as sql
import numpy as np

from _to_df import to_df
from _merge import merge
from _aggregate import aggregate
from _shard import shard
from _pci_wld_eci import pci_wld_eci
from _domestic_eci import domestic_eci
from _calc_diversity import calc_diversity
from _brazil_rca import brazil_rca
from _rdo import rdo
from _growth import calc_growth
from _column_lengths import add_column_length

def comtrade_validation(ctx, param, value):
    try:
        st = os.stat(value)
    except OSError:
        raise click.BadParameter('Path "{}" does not exist. Did you forget to run the COMTRADE scripts for this year?'.format(value))
    return value

@click.command()
@click.argument('export_file_path', type=click.Path(exists=True))
@click.argument('import_file_path', type=click.Path(exists=True))
@click.option('-y', '--year', prompt='Year', help='year of the data to convert', required=True)
@click.option('eci_file_path', '--eci', '-e', type=click.Path(), required=True, prompt="Path to ECI file", callback=comtrade_validation)
@click.option('pci_file_path', '--pci', '-p', type=click.Path(), required=True, prompt="Path to PCI file", callback=comtrade_validation)
@click.option('ypw_file_path', '--ypw', '-r', type=click.Path(), required=True, prompt="Path to YPW file", callback=comtrade_validation)
@click.option('output_path', '--output', '-o', help='Path to save files to.', type=click.Path(), required=True, prompt="Output path")
def main(export_file_path, import_file_path, year, eci_file_path, pci_file_path, ypw_file_path, output_path):
    start = time.time()
    step = 0
    
    depths = {
        "bra": [1, 3, 5, 7, 9],
        "hs": [2, 6],
        "wld": [2, 5]
    }
    
    if not os.path.exists(output_path): os.makedirs(output_path)
    d = pd.HDFStore(os.path.join(output_path, 'secex.h5'))
    # if "ymb" in d:
    if "ymbp" in d:
        tables = {}
        tables["ymb"] = d["ymb"]; tables["ymp"] = d["ymp"]; tables["ymw"] = d["ymw"]; tables["ymbp"] = d["ymbp"]; tables["ymbw"] = d["ymbw"]; tables["ympw"] = d["ympw"]; tables["ymbpw"] = d["ymbpw"]
    else:
        step += 1; print '''\nSTEP {0}: \nImport file to pandas dataframe'''.format(step)
        secex_exports = to_df(export_file_path, False)
        secex_imports = to_df(import_file_path, False)
        # secex_exports = secex_exports.head(1000)
        # secex_imports = secex_imports.head(1000)

        step += 1; print '''\nSTEP {0}: \nMerge imports and exports'''.format(step)
        secex_df = merge(secex_exports, secex_imports)

        step += 1; print '''\nSTEP {0}: \nAggregate'''.format(step)
        ymbpw = aggregate(secex_df)

        step += 1; print '''\nSTEP {0}: \nShard'''.format(step)
        [ymb, ymbp, ymbw, ymp, ympw, ymw] = shard(ymbpw)

        step += 1; print '''\nSTEP {0}: \nCalculate PCI & ECI'''.format(step)
        [ymp, ymw] = pci_wld_eci(eci_file_path, pci_file_path, ymp, ymw, year)

        step += 1; print '''\nSTEP {0}: \nCalculate diversity'''.format(step)
        ymb = calc_diversity(ymbp, ymb, "bra_id", "hs_id")
        ymb = calc_diversity(ymbw, ymb, "bra_id", "wld_id")
        ymp = calc_diversity(ymbp, ymp, "hs_id", "bra_id")
        ymp = calc_diversity(ympw, ymp, "hs_id", "wld_id")
        ymw = calc_diversity(ymbw, ymw, "wld_id", "bra_id")
        ymw = calc_diversity(ympw, ymw, "wld_id", "hs_id")
        
        step += 1; print '''\nSTEP {0}: \nCalculate domestic ECI'''.format(step)
        ymb = domestic_eci(ymp, ymb, ymbp, depths["bra"])

        step += 1; print '''\nSTEP {0}: \nCalculate Brazilian RCA'''.format(step)
        ymp = brazil_rca(ymp, ypw_file_path, year)
    
        step += 1; print '''\nSTEP {0}: \nCalculate RCA, diversity and opp_gain aka RDO'''.format(step)
        ymbp = rdo(ymbp, ymp, year, depths["bra"], ypw_file_path)
        
        tables = {"ymb": ymb, "ymp": ymp, "ymw": ymw, "ymbp": ymbp, "ymbpw": ymbpw, "ymbw": ymbw, "ympw": ympw}
        for tbln, tbl in tables.items():
            d[tbln] = tbl

    print "computing column lengths"
    for table_name, table_data in tables.items():
        tables[table_name] = add_column_length(table_name, table_data)
    
    print '''\nFINAL STEP: \nSave files to output path'''
    for t_name, t in tables.items():
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        new_file_path = os.path.abspath(os.path.join(output_path, "{0}.tsv.bz2".format(t_name)))
        t.to_csv(bz2.BZ2File(new_file_path, 'wb'), sep="\t", index=True)

    total_run_time = (time.time() - start) / 60
    print; print;
    print "Total runtime: {0} minutes".format(int(total_run_time))
    print; print;

if __name__ == "__main__":
    main()