from copy import deepcopy
from typing import List

import pandas as pd

from cw2 import job, scheduler, util


class Loader(scheduler.AbstractScheduler):
    def run(self, overwrite: bool = False):
        cw_res = CWResult()

        for j in self.joblist:
            cw_res._load_job(j)

        cw_res._compile()
        return cw_res

# TODO: Use https://pandas.pydata.org/pandas-docs/stable/development/extending.html isntead?


class CWResult():
    def __init__(self, df: pd.DataFrame = None):
        self.data_list = []
        self.df = df

    def _compile(self):
        self.df = pd.DataFrame(self.data_list)
        self.data_list = None

    def _load_job(self, j: job.Job) -> None:
        job_config = deepcopy(j.config)
        job_dict = {}
        job_dict['name'] = job_config['name']

        job_dict.update(util.flatten_dict(job_config['params']))

        for r in j.repetitions:
            rep_data = j.load_rep(r)
            rep_data.update({'r': r, 'rep_path': j.get_rep_path(r)})
            rep_data.update(job_dict)
            self.data_list.append(rep_data)

    def data(self) -> pd.DataFrame:
        return self.df

    def filter(self, param_dict: dict):
        df = self.df.cw2.filter(param_dict)
        return CWResult(df)

    def get_repetition(self, r: int):
        df = self.df.cw2.repetition(r)
        return CWResult(df)


@pd.api.extensions.register_dataframe_accessor("cw2")
class Cw2Accessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    
    def filter(self, param_dict: dict):
        flattened = util.flatten_dict(param_dict)

        df = self._obj.copy()
        for k,v in flattened.items():
            df = df[df[k] == v]
        return df

    def repetition(self, r: int):
        df = self._obj
        return df[df['r'] == r]