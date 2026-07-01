"""Generate the UV-Vis / Beer-Lambert workshop dataset.

Produces a synthetic-but-physically-honest calibration series plus one "unknown",
built so that the workshop's engineered lesson lands exactly:

  * The naive pipeline (read the raw peak absorbance, skip baseline correction)
    fits a *gorgeous* calibration line (R2 ~ 0.999) and then predicts the unknown
    ~20% wrong -- because the unknown's baseline differs from the calibration set.
  * Baseline-correcting first recovers the true concentration to within tolerance.

Ground truth is exact because we define it. The data still looks like real messy
lab output (per-spectrum sloping baseline + noise). Deterministic via a fixed seed
so every attendee -- and the presenter's benchmark numbers -- match.

Run:  python generate_data.py
Writes CSVs + a hidden ground_truth.txt into ./data/ next to this script.
"""

from pathlib import Path
import numpy as np

# --- Physics (real values for methylene blue) --------------------------------
EPSILON = 95_000.0      # molar absorptivity, M^-1 cm^-1
PATH = 1.0              # path length, cm
LAMBDA_MAX = 664.0      # absorption peak, nm
PEAK_SIGMA = 20.0       # peak width, nm

WAVELENGTHS = np.arange(400.0, 800.0 + 1.0, 1.0)   # nm, clean baseline both sides of the peak

# --- Sample design -----------------------------------------------------------
CAL_CONCS_UM = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]    # known calibration concentrations
UNKNOWN_CONC_UM = 9.0                              # the answer -- revealed only at milestone M4

# Baselines. Calibration spectra share a low, tight baseline (so the naive
# calibration looks perfect). The unknown was "measured on a different day" --
# a markedly higher, more scattering baseline. That mismatch is the whole trap.
CAL_BASELINE_OFFSET = 0.05      # AU at 400 nm, mean across calibration spectra
CAL_BASELINE_OFFSET_SD = 0.008  # small spread -> R2 stays ~0.999
CAL_BASELINE_SLOPE = -5.0e-5    # AU / nm (gentle downward tilt)
CAL_BASELINE_SLOPE_SD = 1.0e-5
UNKNOWN_BASELINE_OFFSET = 0.221  # tuned so baseline at 664 nm sits ~0.17 AU above the cal mean
UNKNOWN_BASELINE_SLOPE = -5.0e-5

NOISE_SD = 0.004                # AU, detector noise

SEED = 42
HERE = Path(__file__).resolve().parent
OUT = HERE / "data"


def peak(conc_um):
    """Beer-Lambert Gaussian peak: height = epsilon * l * c."""
    height = EPSILON * PATH * (conc_um * 1e-6)
    return height * np.exp(-((WAVELENGTHS - LAMBDA_MAX) ** 2) / (2 * PEAK_SIGMA**2))


def baseline(offset, slope):
    return offset + slope * (WAVELENGTHS - WAVELENGTHS[0])


def spectrum(conc_um, offset, slope, rng):
    return peak(conc_um) + baseline(offset, slope) + rng.normal(0.0, NOISE_SD, WAVELENGTHS.size)


def save_spectrum(path, absorbance):
    rows = np.column_stack([WAVELENGTHS, absorbance])
    np.savetxt(path, rows, delimiter=",", header="wavelength_nm,absorbance", comments="", fmt="%.4f")


# --- Reference pipelines (INSTRUCTOR ONLY -- attendees write their own) -------
# These exist so the presenter knows the exact expected numbers for this seed.

def read_raw_peak(absorbance):
    """Naive: the raw maximum. Includes whatever baseline is under the peak."""
    return absorbance.max()


def read_corrected_peak(absorbance):
    """Baseline-corrected: fit a line through off-peak anchor regions and subtract,
    then read the peak height at LAMBDA_MAX."""
    anchor = (WAVELENGTHS <= 520) | (WAVELENGTHS >= 760)   # regions with no dye absorption
    coeffs = np.polyfit(WAVELENGTHS[anchor], absorbance[anchor], 1)
    corrected = absorbance - np.polyval(coeffs, WAVELENGTHS)
    return corrected[np.argmin(np.abs(WAVELENGTHS - LAMBDA_MAX))]


def calibrate_and_predict(reader, cal_spectra, unknown_spec):
    x = np.array(CAL_CONCS_UM)
    y = np.array([reader(s) for s in cal_spectra])
    slope, intercept = np.polyfit(x, y, 1)
    r2 = 1 - np.sum((y - (slope * x + intercept)) ** 2) / np.sum((y - y.mean()) ** 2)
    pred = (reader(unknown_spec) - intercept) / slope
    return pred, r2


def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    # Calibration series -> one CSV per sample + an index sheet (filename -> conc).
    cal_spectra = []
    index_lines = ["filename,concentration_uM"]
    for i, conc in enumerate(CAL_CONCS_UM, start=1):
        offset = rng.normal(CAL_BASELINE_OFFSET, CAL_BASELINE_OFFSET_SD)
        slope = rng.normal(CAL_BASELINE_SLOPE, CAL_BASELINE_SLOPE_SD)
        spec = spectrum(conc, offset, slope, rng)
        cal_spectra.append(spec)
        fname = f"calibration_{i:02d}.csv"
        save_spectrum(OUT / fname, spec)
        index_lines.append(f"{fname},{conc:g}")
    (OUT / "calibration_index.csv").write_text("\n".join(index_lines) + "\n")

    # The unknown -- no concentration disclosed anywhere in the handout.
    unknown_spec = spectrum(UNKNOWN_CONC_UM, UNKNOWN_BASELINE_OFFSET, UNKNOWN_BASELINE_SLOPE, rng)
    save_spectrum(OUT / "unknown.csv", unknown_spec)

    # Instructor benchmark numbers for this seed.
    naive_pred, naive_r2 = calibrate_and_predict(read_raw_peak, cal_spectra, unknown_spec)
    corr_pred, corr_r2 = calibrate_and_predict(read_corrected_peak, cal_spectra, unknown_spec)
    naive_err = 100 * (naive_pred - UNKNOWN_CONC_UM) / UNKNOWN_CONC_UM
    corr_err = 100 * (corr_pred - UNKNOWN_CONC_UM) / UNKNOWN_CONC_UM

    (OUT / "ground_truth.txt").write_text(
        "GROUND TRUTH -- do not hand out before milestone M4\n"
        "=================================================\n"
        f"Unknown true concentration : {UNKNOWN_CONC_UM:.3f} uM\n"
        f"Molar absorptivity (epsilon): {EPSILON:,.0f} M^-1 cm^-1\n"
        f"Path length                : {PATH:g} cm\n"
        f"Peak wavelength            : {LAMBDA_MAX:g} nm\n"
        f"Calibration concentrations : {', '.join(f'{c:g}' for c in CAL_CONCS_UM)} uM\n"
        f"Random seed                : {SEED}\n\n"
        "Expected results for this seed (reference pipelines):\n"
        f"  Naive (no baseline correction): predicts {naive_pred:.2f} uM  "
        f"(error {naive_err:+.1f} %),  calibration R2 = {naive_r2:.4f}\n"
        f"  Baseline-corrected           : predicts {corr_pred:.2f} uM  "
        f"(error {corr_err:+.1f} %),  calibration R2 = {corr_r2:.4f}\n\n"
        "The lesson: the naive calibration looks near-perfect (high R2) yet the\n"
        "prediction is confidently wrong. Only the benchmark against this true value\n"
        "exposes it. A good skill bakes that check in and fails loudly.\n"
    )

    print(f"Wrote {len(CAL_CONCS_UM)} calibration spectra + unknown + index to {OUT}")
    print(f"  naive     : {naive_pred:5.2f} uM ({naive_err:+.1f} %)  R2={naive_r2:.4f}")
    print(f"  corrected : {corr_pred:5.2f} uM ({corr_err:+.1f} %)  R2={corr_r2:.4f}")
    print(f"  truth     : {UNKNOWN_CONC_UM:5.2f} uM  (hidden in data/ground_truth.txt)")


if __name__ == "__main__":
    main()
