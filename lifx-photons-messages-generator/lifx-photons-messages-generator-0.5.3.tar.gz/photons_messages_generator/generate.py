from photons_messages_generator.adjustments import Adjustments
from photons_messages_generator.helpers import snake_to_camel
from photons_messages_generator.resolver import Resolver
from photons_messages_generator.src import Src
from photons_messages_generator import errors

from input_algorithms.meta import Meta
from collections import defaultdict
import fnmatch
import logging
import json
import os

log = logging.getLogger("generator.generate")

def write_enums(options, src, adjustments, output_folder):
    with options.file(output_folder) as write_line:
        if options.static:
            write_line(options.static.strip())
            write_line("")

        for i, enum in enumerate(src.enums):
            write_line(f"class {enum.name}(Enum):")
            for value in enum.values:
                write_line(f"    {value.name} = {value.value}")

            if i != len(src.enums) - 1:
                write_line("")

def write_fields(options, src, adjustments, output_folder):
    with options.file(output_folder) as write_line:
        if options.static:
            write_line(options.static.strip())
            write_line("")

        for options in adjustments.types.values():
            write_line(f"{options.name} = {options.format(in_fields=True)}")
            write_line("")

        want = []
        for i, struct in enumerate(src.groups):
            if struct.full_name not in adjustments.ignore:
                want.append(struct)

        for num, struct in enumerate(want):
            write_line(f"{struct.name} = [")
            for i, field in enumerate(struct.item_fields):
                indent = "    , "
                if i == 0:
                    indent = indent.replace(",", " ")
                write_line(f"{indent}{field.format(in_fields=True)}")
            write_line("    ]")

            if num != len(want) - 1:
                write_line("")

            if struct.many_options is not None:
                if num == len(want) - 1:
                    write_line("")

                write_line(f"class {struct.many_name}(dictobj.PacketSpec):")
                write_line(f"    fields = {struct.name}")
                if struct.many_options.cache_amount is not None:
                    write_line(f"{struct.many_name}.Meta.cache = LRU({struct.many_options.cache_amount})")

                if num != len(want) - 1:
                    write_line("")

def write_messages_class(write_line, namespace, packets, src, adjustments):
    write_line("#" * 24)
    write_line(f"###   {namespace.upper()}")
    write_line("#" * 24)
    write_line("")
    klsname = f"{snake_to_camel(namespace)}Messages"
    write_line(f"class {klsname}(Messages):")
    for packet in packets:
        parent = adjustments.changes.get(packet.full_name)

        if parent and parent.using is not None:
            write_line(f"    {packet.name} = {parent.using.name}.using({packet.pkt_type})")
            write_line("")
            continue

        multi = None
        if parent and parent.multi is not None:
            multi = parent.multi

        has_fields = multi or len(packet.item_fields) > 0
        end = "" if has_fields else ")"
        write_line(f"    {packet.name} = msg({packet.pkt_type}{end}")
        for field in packet.item_fields:
            write_line(f"        , {field.format()}")
        if multi:
            if len(packet.item_fields) > 0:
                write_line("")
            lines = multi.strip().split("\n")
            write_line(f"        , multi = {lines[0]}")
            for line in lines[1:]:
                write_line(f"         {line}")
        if has_fields:
            write_line("        )")
        write_line("")

    return klsname

def write_packets(options_list, src, adjustments, output_folder):
    by_namespace = defaultdict(list)
    for packet in src.packets:
        by_namespace[packet.namespace].append(packet)

    def match_namespaces(opts):
        matched = []
        for namespace in by_namespace:
            if any(fnmatch.fnmatch(namespace, m) for m in opts.include):
                matched.append(namespace)
        matched = [namespace for namespace in matched
              if not any(fnmatch.fnmatch(namespace, m) for m in opts.exclude)
            ]

        ordered = [ns for ns in adjustments.namespace_order if ns in matched]
        ordered += [ns for ns in matched if ns not in ordered]
        return ordered

    by_output = {}
    for options in options_list:
        t = tuple(options.dest)
        if t in options:
            raise errors.InvalidOutput("Defined output for the same file multiple times", dest=t)

        by_output[t] = match_namespaces(options.options)

    found = []
    for t, namespaces in by_output.items():
        dupd = [ns for ns in namespaces if ns in found]
        if dupd:
            raise errors.InvalidOutput("namespaces have been declared multiple times", duplicated=dupd)
        found.extend(namespaces)

    for options in options_list:
        with options.file(output_folder) as write_line:
            if options.static:
                write_line(options.static.strip())
                write_line("")

            klses = []

            for namespace in by_output[tuple(options.dest)]:
                packets = sorted(by_namespace[namespace], key=lambda pkt: pkt.pkt_type)
                klses.append(write_messages_class(write_line, namespace, packets, src, adjustments))

            write_line(f"__all__ = {json.dumps(klses)}")

def generate(src, adjustments, output_folder):
    if "fields" in src:
        src["groups"] = src["fields"]
    src = Src.FieldSpec().normalise(Meta({}, []).at("src"), src)

    adjustments = Adjustments.FieldSpec().normalise(Meta({}, []).at("adjustment"), adjustments)

    Resolver(src, adjustments).resolve()

    if os.environ.get("NO_OUTPUT") == "1":
        return

    by_type = defaultdict(list)
    for options in adjustments.output:
        by_type[options.create].append(options)

    for t in ("enums", "fields"):
        if len(by_type[t]) != 1:
            raise errors.InvalidOutput(f"Must specify {t} output only once", found=len(by_type[t]))
        by_type[t] = by_type[t][0]

    log.info("Writing enums")
    write_enums(by_type["enums"], src, adjustments, output_folder)

    log.info("Writing fields")
    write_fields(by_type["fields"], src, adjustments, output_folder)

    log.info("Writing packets")
    write_packets(by_type["packets"], src, adjustments, output_folder)
