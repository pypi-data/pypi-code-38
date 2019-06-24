import opengen as og
import casadi.casadi as cs

u = cs.SX.sym("u", 5)
p = cs.SX.sym("p", 2)
phi = og.functions.rosenbrock(u, p)
bounds = og.constraints.Ball2(None, 1.5)
problem = og.builder.Problem(u, p, phi) \
    .with_penalty_constraints(None)     \
    .with_constraints(bounds)
build_config = og.config.BuildConfiguration()         \
    .with_build_directory(".python_test_build")       \
    .with_build_mode("debug")                         \
    .with_tcp_interface_config()                      \
    .with_build_c_bindings()
meta = og.config.OptimizerMeta()                      \
    .with_optimizer_name("new_optimizer")
builder = og.builder.OpEnOptimizerBuilder(problem,
                                          metadata=meta,
                                          build_configuration=build_config) \
    .with_generate_not_build_flag(False).with_verbosity_level(1)
builder.build()

