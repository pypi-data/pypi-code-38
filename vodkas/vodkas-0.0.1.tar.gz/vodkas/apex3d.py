import subprocess
from pathlib import Path

from vodkas.misc import get_coresNo
import vodkas.default_paths as default


def apex3d(raw_folder,
           output_dir,
           lock_mass_z2=785.8426,
           lock_mass_tol_amu=.25,
           low_energy_thr=300,
           high_energy_thr=30,
           lowest_intensity_thr=750,
           write_xml=True,
           write_binary=True,
           write_csv=False,
           max_used_cores=get_coresNo(),
           path_to_apex3d=default.apex3Dpath,
           PLGS=True,
           cuda=False,
           unsupported_gpu=False,
           **kwds):
    """A wrapper around the infamous Apex3D.
    
    Args:
        raw_folder (Path or str): a path to the input folder with raw Waters data.
        output_dir (Path or str): Path to where to place the output.
        lock_mass_z2 (float): The lock mass for doubly charged ion (which one, dunno, but I guess a very important one).
        lock_mass_tol (float): Tolerance around lock mass (in atomic mass units, amu).
        low_energy_thr (int): The minimal intensity of a precursor ion so that it ain't a noise peak.
        high_energy_thr (int): The minimal intensity of a fragment ion so that it ain't a noise peak.
        lowest_intensity_thr (int): The minimal intensity of a peak to be analyzed.
        write_xml (boolean): Write the output in an xml in the output folder.
        write_binary (boolean): Write the binary output in an xml in the output folder.
        write_csv (boolean): Write the output in a csv in the output folder (doesn't work).
        max_used_cores (int): The maximal number of cores to use.
        path_to_apex3d (Path or str): Path to the "Apex3D.exe" executable.
        PLGS (boolean): No idea what it is.
        cuda (boolean): Use CUDA.
        unsupported_gpu (boolean): Try using an unsupported GPU for calculations. If it doesn't work, the pipeline switches to CPU which is usually much slower.
        kwds: other parameters for 'subprocess.run'.
    Returns:
        tuple: the path to the outcome (no extension: choose it yourself and believe more in capitalism) and the completed process.
    """
    algo = str(Path(path_to_apex3d))
    raw_folder = Path(raw_folder)
    output_dir = Path(output_dir)
    process = subprocess.run(["powershell.exe",
        # '$ErrorActionPreference = "Stop"',#error windows stop appearing.
        algo,
        "-pRawDirName {}".format(raw_folder),
        "-outputDirName {}".format(output_dir),
        "-lockMassZ2 {}".format(lock_mass_z2),
        "-lockmassToleranceAMU {}".format(lock_mass_tol_amu),
        "-leThresholdCounts {}".format(int(low_energy_thr)),
        "-heThresholdCounts {}".format(int(high_energy_thr)),
        "-binIntenThreshold {}".format(int(lowest_intensity_thr)),
        "-writeXML {}".format(int(write_xml)),
        "-writeBinary {}".format(int(write_binary)),
        "-bRawCSVOutput {}".format(int(write_csv)),
        "-maxCPUs {}".format(int(max_used_cores)),
        "-PLGS {}".format(int(PLGS)),
        "-bEnableCuda {}".format(int(cuda)),
        "-bEnableUnsupportedGPUs {}".format(int(unsupported_gpu)) ],
        **kwds)
    out_bin = output_dir/(raw_folder.stem + "_Apex3D.bin")
    out_xml = out_bin.with_suffix('.xml')
    if not out_bin.exists() and not out_xml.exists():
        raise RuntimeError("Apex3D failed: output is missing")
    if process.stderr:
        print(process.stderr)
        raise RuntimeError("Apex3D failed: WTF")
    if kwds.get('capture_output', False):# otherwise no input was caught.
        log = output_dir/"apex3d.log"
        log.write_bytes(process.stdout)
    return out_bin.with_suffix(''), process


def test_apex3d():
    """test the stupid Apex3D."""
    apex3d(Path("C:/ms_soft/MasterOfPipelines/RAW/O1903/O190302_01.raw"),
           Path("C:/ms_soft/MasterOfPipelines/test/apex3doutput"))



if __name__ == "__main__":
    test_apex3d()