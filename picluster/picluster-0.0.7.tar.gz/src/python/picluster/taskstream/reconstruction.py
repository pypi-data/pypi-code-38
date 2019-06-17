from .monte_carlo import MonteCarloSimulation
from .combinator import sequential
from . import cli
from . import premitive as p


def reconstruction(
    work_directory: "Path",
    sinogram: Resource["Sinogram"],
    config: "JSON/Dict",
    system_matrix=None,
) -> Task[Resource["Image"]]:
    return sequential(
        lambda _: p.query(sinogram),
        lambda sinogram: cli.mkdir(work_directory).switch_map(
            lambda d: of({"directory": d, "sinogram": sinogram})
        ),
        lambda inputs: srf(inputs['direct ory'], inputs['sinogram'])
    )


def simulation_and_reconstruction(
    work_directory, phantom: Resource["File"], simulation_config, reconstruction_config
):
    return (
        p.query(phantom)
        .switch_map(
            lambda q: MonteCarloSimulation(
                work_directory, 100, simulation_config, ["material.xml", q]
            )
        )
        .switch_map(lambda sino: reconstruction(work_directory))
    )


def make_sub_directories_and_run_task(
    root: "Path", nb_sub_directories: int, task_creator: "(d, i)=> Task", prefix="sub"
) -> Observable[List["Path"]]:
    return cli.mkdir(root).switch_map(
        lambda d: parallel(
            [
                cli.mkdir(d / f"{prefix}.{i}").switch_map(lambda d: task_creator(d))
                for i in range(nb_sub_directories)
            ]
        )
    )


def psf(
    workdir: "Path",
    phantom: Resource["File"],
    psf_config,
    simulation_config,
    recon_config,
):
    root = mkdir(workdir)
    point_results = sqeuential(
        lambda _: root,
        lambda d: cli.mkdir(d / "simulations"),
        lambda d: make_sub_directories_and_run_task(
            d,
            300,
            lambda d, i: psf_one_point(
                d, psf_config, i, simulation_config, recon_config
            ),
        ),
    )  # 300 point source reconstruction images
    fitted_psf_parameters = sequential(
        lambda _: parallel([map(p.query, point_results)]),
        lambda images: mixture_of_gaussian_fit(images),
        p.create,
    )
    phantom_sino = sequntial(
        lambda _: parallel([root, p.query(phantom)]),
        lambda result: MonteCarloSimulation(
            result[0], 100, simulation_config, ["Some extra files", result[1]]
        ),
    )

    # Configs are auto combined here
    recon_config_combined = dict(recon_config)
    recon_config_combined.update(simulation_config)
    recon_config_combined.update(psf_config)

    return sequential(
        lambda _: parallel(
            [
                fitted_psf_parameters.switch_map(lambda p: create_system_matrix(p)),
                phantom_sino,
            ]
        ),
        lambda result: reconstruction(workdir, result[1], recon_config, result[0]),
        p.create,
    )



def pse_one_point(d: workdir, psf_config, index, simulation_config, recon_config):
    # Configs are auto combined here
    recon_config_combined = dict(recon_config)
    recon_config_combined.update(simulation_config)

    return squential(
        lambda _: create_point_source(d, psf_config, index),
        lambda phantom: simulation_and_reconstruction(
            d, phantom, simulation_config, recon_config
        ),
    )

