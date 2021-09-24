# Starter Kit to Perform Light Curve fits of DC2 with SNCosmo/SNEMO

## Overview

Use SNEMO (via SNComso) to fit the DC2 photometry. This will allow, at a later date, for a user to choice in SNCosmo modle. First this codebase will be developed for the use of `snemo2`and `snemo7`, with a goal of allowing any SNCosmo model.

## Setup

Use this script with the base DESC-SN Cori environment:
```shell
source /global/cfs/cdirs/lsst/groups/SN/software/setup_sn_all.sh
```

## Basic Usage

From `$SNANA_LSST_ROOT/starterKits/DC2+SNEMO` on Cori, (using the DESC `base` SN conda env) run `python fit_lc.py`. Light-curve fits will be found in `snemo2.FITRES` and `snemo2.csv` with errors recorded in `ERROR.log`.

Currently, without optimization, it takes ~15 mins to fit 50 SNe.

## Tutorials/Documentation

Tutorials and documenation in `/docs/` are hosted on GitHub pages at https://benjaminrose.github.io/DC2-SNEMO/.


## Outputs

* Batch job 47473881 producecd `snemo2_v0.1` output for the first 200 SNe in DC2 (172 where fit).