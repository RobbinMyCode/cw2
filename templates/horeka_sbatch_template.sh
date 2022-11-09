#!/bin/bash
#SBATCH -p %%partition%%
#SBATCH -A %%account%%
#SBATCH -J %%job-name%%
#SBATCH --array 0-%%last_job_idx%%%%%num_parallel_jobs%%

# Please use the complete path details :
#SBATCH -D %%experiment_execution_dir%%
#SBATCH -o %%slurm_log%%/out_%A_%a.log
#SBATCH -e %%slurm_log%%/err_%A_%a.log

# Cluster Settings
#SBATCH -n 4     # Number of tasks
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-tasks=%%cpus-per-task%%  # Number of cores per task
#SBATCH -t %%time%%             # 1:00:00 Hours, minutes and seconds, or '#SBATCH -t 10' - only minutes

%%sbatch_args%%
# -------------------------------

# Activate the virtualenv / conda environment
%%venv%%


# Export Pythonpath
%%pythonpath%%

# Additional Instructions from CONFIG.yml
%%sh_lines%%

python3 %%python_script%% %%path_to_yaml_config%% -j $((4 * $SLURM_ARRAY_TASK_ID)) %%cw_args%% &
python3 %%python_script%% %%path_to_yaml_config%% -j $((4 * $SLURM_ARRAY_TASK_ID + 1)) %%cw_args%% &
python3 %%python_script%% %%path_to_yaml_config%% -j $((4 * $SLURM_ARRAY_TASK_ID + 2)) %%cw_args%% &
python3 %%python_script%% %%path_to_yaml_config%% -j $((4 * $SLURM_ARRAY_TASK_ID + 3)) %%cw_args%% &

wait


# THIS WAS BUILT FROM THE DEFAULLT SBATCH TEMPLATE