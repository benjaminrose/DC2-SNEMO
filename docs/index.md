# Fitting DC2 data with SNCosmo

Tutorials are coming later.

## Instalation

Make sure you are using the DESC Time Domain working group's `conda` enviornment.

```shell
source /global/cfs/cdirs/lsst/groups/SN/software/setup_sn_all.sh
```

## Usage

In the project driectry, you can test that things run via `python fit_lc.py`. 

For a full run use `sbatch batch_fit_lc.sh`. If you want to add this analysis to your own script, add `python fit_lc.py --sn N` or `python fit_lc.py --all`, where N is the number of SN you want to fit. Note that 200 SNe are fit in ~50 mins, so fitting DC2's near 2200 objects with `--all` will take ~10 hours.

For more details, read the script's help message `python fit_lc.py -h`.

Currently only fitting with SNEMO2 is working.

## Inputs

This analysis script requires photometry and redshifts in SNANA sytle fits files. The DC2 data files are currently hardcoded.

## External Resources

- SNEMO defintion
- SNCosmo documentation
- DC2
- DESC pipeline
- DESC Cori enviornment managemnt
