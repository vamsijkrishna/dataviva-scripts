import itertools, sys
import pandas as pd

from _aggregate import agg_rules, median_rules



def shard(ybio, raw):
    ybio_raw =  ybio.reset_index()

    deepestB = ybio_raw['bra_id'].str.len() == 8    
    deepestI = ybio_raw['cnae_id'].str.len() == 6
    deepestO = ybio_raw['cbo_id'].str.len() == 4

    ybi = ybio_raw[deepestO].groupby(['year','bra_id','cnae_id']).agg(agg_rules)
    ybo = ybio_raw[deepestI].groupby(['year','bra_id','cbo_id']).agg(agg_rules)
    yio = ybio_raw[deepestB].groupby(['year','cnae_id','cbo_id']).agg(agg_rules)

    yb = ybio_raw[deepestI & deepestO].groupby(['year','bra_id']).agg(agg_rules)
    yi = ybio_raw[deepestB & deepestO].groupby(['year','cnae_id']).agg(agg_rules)
    yo = ybio_raw[deepestB & deepestI].groupby(['year','cbo_id']).agg(agg_rules)

    tbls = {"yb": yb, "yi": yi, "yo": yo, "ybi": ybi, "ybio": ybio, "ybo": ybo, "yio": yio}

    # for each dataset, we need to go back to the raw data
    lookup = {"b":"bra_id", "i":"cnae_id", "o":"cbo_id"}
    nestings = {"b":[8,2], "i":[6,1], "o":[4, 1]}

    for t_name, t in tbls.items():
        print t_name
        raw_data_for_median = pd.DataFrame()
        my_nesting = [nestings[i] for i in t_name if i is not "y"]
        my_nesting_cols = [lookup[i] for i in t_name if i is not "y"]

        for depths in itertools.product(*my_nesting):
            my_raw = raw.copy()
            my_raw["wage_med"] = my_raw["wage"]
            my_raw["age_med"] = my_raw["age"]
            my_raw["edu_mode"] = my_raw["literacy"]
            print depths

            for col_name, d in zip(my_nesting_cols, depths):
                my_raw[col_name] = my_raw[col_name].apply(lambda x: x[:d])

            pk = ["year"] + my_nesting_cols
            temp = my_raw.groupby(pk).agg(median_rules)
            raw_data_for_median = pd.concat([raw_data_for_median, temp])

        mynewtable = pd.merge(t, raw_data_for_median, how='left', left_index=True, right_index=True)
        tbls[t_name] = mynewtable
        print tbls[t_name].head()
    return tbls

