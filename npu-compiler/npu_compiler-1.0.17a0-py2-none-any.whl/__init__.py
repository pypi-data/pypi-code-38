#coding: utf-8

from npu_compiler.config import Config
from npu_compiler.compiler import run
from npu_compiler.freeze_graph_ckpt import freeze_pb as freeze

def compile_npu(pb_file, config_file):
    Config.parse_config(config_file, {"VERBOSE":False})
    Config.parse_para()
    Config.check_config()
    run()

def freeze_pb(graph_file, ckpt_file, pb_file, output_ops):
    freeze(graph_file, ckpt_file, pb_file, output_ops)
