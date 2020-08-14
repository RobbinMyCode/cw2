import logging
from typing import List

from cw2 import (cli_parser, config, cw_loading, cw_logging, cw_slurm,
                 experiment, job, scheduler)


class ClusterWork():
    def __init__(self, exp_cls: experiment.AbstractExperiment = None):
        self.args = cli_parser.Arguments().get()
        self.exp_cls = exp_cls
        self.config = config.Config(self.args.config, self.args.experiments)

        self.logArray = cw_logging.LoggerArray()
        self.joblist = None

    def add_logger(self, logger: cw_logging.AbstractLogger) -> None:
        """add a logger to the ClusterWork pipeline

        Args:
            logger (cw_logging.AbstractLogger): logger object to be called during execution
        """
        self.logArray.add(logger)

    def _get_jobs(self, delete: bool = False, root_dir: str = "") -> List[job.Job]:
        """private method. creates and returns all configured jobs.

        Args:
            delete (bool, optional): delete all old data inside the job directories. Defaults to False.
            root_dir (str, optional): [description]. Defaults to "".

        Returns:
            List[job.Job]: list of all configured job objects
        """
        if self.joblist is None:
            factory = job.JobFactory(self.exp_cls, self.logArray, delete, root_dir)
            self.joblist = factory.create_jobs(self.config.exp_configs)
        return self.joblist

    def run(self, root_dir: str = ""):
        """Run ClusterWork computations.

        Args:
            root_dir (str, optional): [description]. Defaults to "".
        """
        if self.exp_cls is None:
            raise NotImplementedError(
                "Cannot run with missing experiment.AbstractExperiment Implementation.")

        self.config.to_yaml(relpath=True)

        args = self.args

        # Handle SLURM execution
        if args.slurm:
            s = scheduler.SlurmScheduler(self.config)
        else:
            # Do Local execution
            s = scheduler.LocalScheduler()

        self._run_scheduler(s, root_dir)
        

    def load(self, root_dir: str = "") -> cw_loading.CWResult:
        """Loads all saved information.

        Args:
            root_dir (str, optional): [description]. Defaults to "".

        Returns:
            dict: saved data in dict form. keys are the job's log folders, values are dicts of logger -> data
        """

        loader = cw_loading.Loader()

        return self._run_scheduler(loader, root_dir)


    def _run_scheduler(self, s: scheduler.AbstractScheduler, root_dir: str = ""):
        if self.logArray.is_empty():
            logging.warning("No Logger has been added. Are you sure?")

        args = self.args
        job_list = self._get_jobs(False, root_dir)

        if args.job is not None:
            job_list = [job_list[args.job]]

        s.assign(job_list)        
        return s.run(overwrite=args.overwrite)

        
