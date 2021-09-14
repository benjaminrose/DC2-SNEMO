"""fit_lc.py - 
"""
from datetime import datetime
import os
from pathlib import Path

import numpy as np
from pandas import DataFrame, Series
import sncosmo

# TODO: Are the bandpasses in SNCosmo correct?
# TODO: use wavelength extension of SNEMO to avoid: `RuntimeWarning: Dropping following bands from data:`


__version__ = "v0.1-dev"
__email__ = "benjamin.rose@duke.edu"
__author__ = f"Benjami Rose <{__email__}>"


def read_data(folder):
    """Read light-curve fit files from SNANA generate FITS files.

    Uses `sncosmo.read_snana_fits()`, https://sncosmo.readthedocs.io/en/stable/api/sncosmo.read_snana_fits.html.
    
    Parameters
    ----------
    folder: string
        The folder containing the fits header
    
    Returns
    -------
    list
        Each item in the list is an `astropy.Table` instance containing 
        the FITS metadata and science data for a SN.
    
    TODO
    ----
    - [ ] Remove hard coding of analysis name (DC2_run221)
    - [ ] update to handle data sets split into several files, via *.LIST
    - [ ] Add option to use `read_snana_ascii` for debugging?
    """
    if FITS:
        data = sncosmo.read_snana_fits(
            folder + "/DC2_run22i_FITS_HEAD.FITS.gz",
            folder + "/DC2_run22i_FITS_PHOT.FITS.gz",
            n=MAX_SN,
        )
    return data


def snana_table2sncosmo_table(data):
    """Takes a single data table and converts columns and values to go from
    a DC2 SNANA conventions to a SNCosmo `fit_lc` compliant table.

    For example, converting SNANA "FLUXCAL" to usable fluxes and replacging
    single character band names to SNCosmo keys. 

    Parameters
    ----------
    data: astropy.Table
        An astropy.Table of the SNANA LC meta and sciencd data.
        Assumes to follow output sytle of `sncosmo.read_snana_fits()`.
    
    Returns
    -------
    astropy.Table
        A cleaned up data table with updated columns and values to match

    TODO
    -----
    - [ ] Find a faster way to rename filters. List comprehension is not the best
    """
    # Need SNCosmo data names
    # https://sncosmo.readthedocs.io/en/stable/photdata.html?highlight=%20no%20alias%20found%20for%20%27flux%27#flexible-column-names
    data.rename_column("FLUXCAL", "flux")
    data.rename_column("FLUXCALERR", "fluxerr")
    data.rename_column("ZEROPT", "zp")  # not needed in SNCosmo >=2.7 (PR #321)
    # FLUXCAL assumes a zp of 31.5, always. The zp in the data are irrelevant for this work.
    data["zp"] = 27.5
    data["zpsys"] = "ab"

    # TODO: Find a faster way.
    data["BAND"] = [s.replace("u ", "lsstu") for s in data["BAND"]]
    data["BAND"] = [s.replace("g ", "lsstg") for s in data["BAND"]]
    data["BAND"] = [s.replace("r ", "lsstr") for s in data["BAND"]]
    data["BAND"] = [s.replace("i ", "lssti") for s in data["BAND"]]
    data["BAND"] = [s.replace("z ", "lsstz") for s in data["BAND"]]
    data["BAND"] = [s.replace("Y ", "lssty") for s in data["BAND"]]

    return data


def fit_lc(data, model, mcmc=True):
    """idk
    
    Parameters
    ----------
    data: type
        idk
    model: sncosmo.Model
        idk
    mcmc: bool
        idk
    
    Returns
    -------
    idk
        idk
    """
    fit_results = []

    for sn in data:
        sn = snana_table2sncosmo_table(sn)
        if mcmc:
            # Fit data, and handle certain errors.
            try:
                print(f"Fitting {sn.meta['SNID'].decode('utf-8')}")
                fit_result, _ = sncosmo.mcmc_lc(
                    sn,
                    model,
                    model.param_names,
                    bounds={
                        "z": (
                            sn.meta["REDSHIFT_FINAL"] - Z_WIDTH,
                            sn.meta["REDSHIFT_FINAL"] + Z_WIDTH,
                        )
                    },
                    minsnr=MINSNR,
                    warn=WARNINGS,
                    # TODO: add prior functions.
                )
            except sncosmo.fitting.DataQualityError:
                message = (
                    f"{sn.meta['SNID'].decode('utf-8')} has no data with S/N > {MINSNR}"
                )
                print(message, end="\n\n")
                error_file.write(message + "\n")
            except RuntimeError as error:
                message = f"{sn.meta['SNID'].decode('utf-8')} at z = {sn.meta['REDSHIFT_FINAL']:.6G} had a runtime error: "
                print(message)
                print(error, end="\n\n")
                error_file.write(message + str(error) + "\n")
            else:
                fit_results.append(fit_result)
        else:
            raise ValueError(
                "Need to use MCMC fitting: default DESC env has `emcee` but not `iminuit`"
            )

        if VERBOSE:
            print(sn.meta["SNID"].decode("utf-8"))
            print("---------------")
            print("input redshift:", sn.meta["REDSHIFT_FINAL"])
            print("")
            for i, j, k in zip(
                fit_result.param_names,
                fit_result.parameters,
                fit_result.errors.values(),
            ):
                # .errors is an ordered dictionary. Everything is ok.
                print(f"{i}: {j:.3G} +/ {k:.2G}")
            print("")

    return fit_results


def combin_and_tidy(data_tables, fit_results):
    """Take input (meta) data and fit results and make a tidy data table"""
    # Build initial DataFrame with photometry metadata, fit parameters, uncertainties, and fitting keys
    # Pass along all input keys. Prepend `MODEL-NAME_` to all new keys.
    tidy_data = DataFrame(data_tables[0].meta, index=[0])
    tidy_data[
        np.char.add(f"{MODEL.upper()}_", fit_results[0].param_names)
    ] = fit_results[0].parameters
    # TODO: add uncertainties
    # TODO: add fitting parameters like mean_acceptance_fraction

    # Add a data row for each subsiquent SN after checking length of data
    if len(data_tables) == 1:
        return tidy_data
    for data, fit in zip(data_tables[1:], fit_results[1:]):
        next_index = len(tidy_data.index)

        tidy_data.loc[next_index] = Series(data.meta)
        tidy_data.loc[
            next_index, np.char.add(f"{MODEL.upper()}_", fit.param_names)
        ] = fit.parameters
        # Add  paramter errors and fitting parameters

    # Convert bite-strings to string-strings
    # Sadly this is not done inplace.
    tidy_data[["SUBSURVEY", "SNID", "IAUC"]] = tidy_data[
        ["SUBSURVEY", "SNID", "IAUC"]
    ].applymap(lambda x: x.decode("utf-8"))

    if VERBOSE:
        print(tidy_data[["SNID", "SNEMO2_z", "SNEMO2_As"]])

    return tidy_data


def save_fits(tidy_data, file_path, format="fitres"):
    """description
    
    Parameters
    ----------
    tidy_data : pandas.DataFrame
        Following the tidy data convention of one object per row.
    file_path: str
        Include full absolute path, and filename but not format.
        For example "path/to/file/output" would (default) to the
        output being saved to "path/to/file/output.FITRES".
    format: str, default="fitres"
    
    Returns
    -------
    
    """

    if format == "fitres":
        _save_as_fitres(tidy_data, file_path + ".FITRES")
    elif format == "csv":
        _save_as_csv(tidy_data, file_path + ".csv")
    elif format == "both":
        _save_as_fitres(tidy_data, file_path + ".FITRES")
        _save_as_csv(tidy_data, file_path + ".csv")
    else:
        raise ValueError("Option `format` can only save fits to `fitres` or `csv`.")


def _save_as_fitres(tidy_data, file_path):
    # add FITRES keys, but don't propicate it back to previous objects
    data = tidy_data.copy()
    data.insert(0, "VARNAMES:", "SN:")

    with open(file_path, "w") as f:
        f.write(f"# Made with SNEMO_FIT {__version__}\n")
        data.to_csv(f, sep=" ", float_format="%.6G", index=False)


def _save_as_csv(tidy_data, file_path):
    with open(file_path, "w") as f:
        f.write(f"# Made with SNEMO_FIT {__version__}\n")
        tidy_data.to_csv(f, float_format="%.6G", index=False)


def main():
    data_set = read_data(DATA_LOCATION)
    fit_results = fit_lc(data_set, sncosmo.Model(source=MODEL), MCMC)
    tidy_data = combin_and_tidy(data_set, fit_results)
    save_fits(tidy_data, f"{OUTPUT_LOCATION}/{MODEL}", "both")


if __name__ == "__main__":
    MODEL = "snemo2"
    DATA_LOCATION = "/global/cfs/cdirs/lsst/groups/SN/snana/SURVEYS/LSST/ROOT/lcmerge/DC2_run22i_FITS"
    ERROR_FILE_PATH = os.getcwd() + "/ERROR.log"
    OUTPUT_LOCATION = os.getcwd()
    FITS = True  # Read FITS data files (instead of ascii files)
    MCMC = True  # DESC SN conda env does not have iminuit, need to use emcee
    Z_WIDTH = 0.002
    MAX_SN = 25
    MINSNR = 3  # Overides SNCosmo's default of 5.
    WARNINGS = False
    VERBOSE = False

    now = datetime.now()
    print(ERROR_FILE_PATH)
    with open(ERROR_FILE_PATH, "w") as error_file:
        error_file.write(f"Running fits with SNEMO_FIT {__version__} on {now}\n")
        main()
