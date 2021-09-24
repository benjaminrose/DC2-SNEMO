#!/bin/bash

# sbatch batch_fit_lc.sh : 
#     launch script with
# sqs : 
#     check status of job while running

# Queues and max time
# https://docs.nersc.gov/jobs/policy/#cori-haswell

#SBATCH --nodes=1
#SBATCH --time=1:20:00   #max wall clock time, defaults to 10 mins
#SBATCH --qos=regular   #debug (default) or regular
#SBATCH --constraint=haswell    #need an architecture: haswell, knl
#SBATCH --license=cfs   #ensure the cfs file system is running
#SBATCH --job-name=batch_fit_lc

# Initializaion sources ~/.bashrc
echo "Starging batch_fit_lc at $(date)"
echo -e "--------------------\n"

#200 SNe fit with SNEMO2 takes ~50 mins
python fit_lc.py --sn 200

echo "finished at $(date)$"