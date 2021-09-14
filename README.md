# Starter Kit to Perform Light Curve fits of DC2 with SNCosmo/SNEMO

## Overview

Use SNEMO (via SNComso) to fit the DC2 photometry. This will allow, at a later date, for a user to choice in SNCosmo modle. First this codebase will be developed for the use of `snemo2`and `snemo7`, with a goal of allowing any SNCosmo model.

## Setup

Use the base DESC SN CORI environment:
```shell
source /global/cfs/cdirs/lsst/groups/SN/software/setup_sn_all.sh
```

## Basic Usage

From `$SNANA_LSST_ROOT/starterKits/DC2+SNEMO` on Cori, (using the DESC `base` SN conda env) run `python fit_lc.py`. Light-curve fits will be found in `snemo2.FITRES` and `snemo2.csv` with errors recorded in `ERROR.log`.

## Tutorials/Documentation

Currently in `/docs/` but will be hosted on GitHub pages someday.
