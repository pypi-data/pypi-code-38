#!/usr/bin/env python3
#===============================================================================
# funcgenom.py
#===============================================================================

"""Classes and functions to facilitate functional genomics
analysis
"""

# To do: "format" methods




# Imports ======================================================================

import coloc
import copy
import gzip
import itertools
import json
import math
import operator
import os
import py1kgp
import pyhg19
import re
import scipy.stats
import statistics
import subprocess
import sumstats
import tempfile

from multiprocessing import Pool




# Constants ====================================================================

RSID_REGEX = re.compile('rs[1-9][0-9]+$')




# Class Bootstrapping Function =================================================

def bootstrap(cls):
    cls.bootstrap()
    return(cls)




# Class Definitions ============================================================

class Genome():
    """Class defining an object representing the genome"""
    
    def __init__(self, processes=1):
        self.chromosome = {}
        self.chromosomes = []
        self.processes = processes
    
    def __repr__(self):
        return repr(self.chromosomes)
    
    def __add__(self, genome):
        if self.variants_header.tuple != genome.variants_header.tuple:
            raise Exception(
                'Can\'t add two genomes with different headers, use | for that'
            )
        if set(self.chromosome.keys()) & set(genome.chromosome.keys()):
            raise Exception(
                'Can\'t add two genomes that share a chromosome, use | for that'
            )
        else:
            sum = Genome(processes=min(self.processes, genome.processes))
            sum.variants_header = self.variants_header
            for chromosome in self.chromosomes + genome.chromosomes:
                sum.add_chromosome(chromosome)
            return sum
    
    def __or__(self, genome):
        union = Genome(processes=min(self.processes, genome.processes))
        union.variants_header = self.variants_header + genome.variants_header
        if self.processes > 1:
            chromosomes_to_unify = set()
        for chromosome_name in tuple(range(1,23)) + ('X', 'Y', 'M'):
            if (
                self.chromosome.get(chromosome_name)
                and (not genome.chromosome.get(chromosome_name))
            ):
                union.add_chromosome(self.chromosome[chromosome_name])
            elif (
                (not self.chromosome.get(chromosome_name))
                and genome.chromosome.get(chromosome_name)
            ):
                union.add_chromosome(genome.chromosome[chromosome_name])
            elif (
                self.chromosome.get(chromosome_name)
                and genome.chromosome.get(chromosome_name)
            ):
                if self.processes == 1:
                    union.add_chromosome(
                        chromosome_union(
                            self.chromosome[chromosome_name],
                            genome.chromosome[chromosome_name],
                            self.variants_header,
                            genome.variants_header,
                            union.variants_header
                        )
                    )
                elif self.processes > 1:
                    chromosomes_to_unify.add(
                        (
                            self.chromosome[chromosome_name],
                            genome.chromosome[chromosome_name],
                            self.variants_header,
                            genome.variants_header,
                            union.variants_header
                        )
                    )
        if self.processes > 1:
            with Pool(
                processes=min(
                    self.processes, genome.processes, len(chromosomes_to_unify)
                )
            ) as pool:
                for chromosome in pool.starmap(
                    chromosome_union, chromosomes_to_unify
                ):
                    union.add_chromosome(chromosome)
        union.processes = min(self.processes, genome.processes)
        return union
    
    def __and__(self, genome):
        intersection = Genome(processes=min(self.processes, genome.processes))
        intersection.variants_header = (
            self.variants_header + genome.variants_header
        )
        if self.processes > 1:
            chromosomes_to_intersect = set()
        for chromosome_name in tuple(range(1,23)) + ('X', 'Y', 'M'):
            if (
                self.chromosome.get(chromosome_name)
                and genome.chromosome.get(chromosome_name)
            ):
                if self.processes == 1:
                    intersection.add_chromosome(
                        chromosome_intersection(
                            self.chromosome[chromosome_name],
                            genome.chromosome[chromosome_name],
                            self.variants_header,
                            genome.variants_header,
                            intersection.variants_header
                        )
                    )
                elif self.processes > 1:
                    chromosomes_to_intersect.add(
                        (
                            self.chromosome[chromosome_name],
                            genome.chromosome[chromosome_name],
                            self.variants_header,
                            genome.variants_header,
                            intersection.variants_header
                        )
                    )
        if self.processes > 1:
            with Pool(
                processes=min(
                    self.processes,
                    genome.processes,
                    len(chromosomes_to_intersect)
                )
            ) as pool:
                for chromosome in pool.starmap(
                    chromosome_intersection,
                    chromosomes_to_intersect
                ):
                    intersection.add_chromosome(chromosome)
        intersection.processes = min(self.processes, genome.processes)
        return intersection
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__init__()
        return False
    
    def __len__(self):
        return len(self.chromosomes)
    
    def variants(self):
        return (
            variant
            for chromosome in self.chromosomes
            for variant in chromosome.variants
        )
    
    def add_chromosome(self, chromosome):
        if isinstance(chromosome, (int, str)):
            chromosome = Chromosome(chromosome)
        self.chromosome[chromosome.int] = chromosome
        self.chromosome[chromosome.char] = chromosome
        self.chromosomes.append(chromosome)
        self.chromosomes.sort()
        self.mafs_have_been_collected = False
    
    def remove_chromosome(self, chromosome):
        if (
            isinstance(chromosome, (int, str))
            and (chromosome in set(self.chromosome.keys()))
        ):
            self.chromosomes.remove(self.chromosome[chromosome])
            chromosome = Chromosome(chromosome)
            del self.chromosome[chromosome.int]
            del self.chromosome[chromosome.char]
        elif chromosome in self.chromosomes:
            self.chromosomes.remove(chromosome)
            del self.chromosome[chromosome.int]
            del self.chromosome[chromosome.char]
    
    def extract_chromosomes(self, *chromosome_names):
        genome = Genome(processes=self.processes)
        genome.variants_header = self.variants_header
        for chromosome_name in chromosome_names:
            genome.add_chromosome(self.chromosome[chromosome_name])
        return genome
        
    def load_loci_from_regions(
        self,
        loci_file_path,
        min_interval_size=None,
        add_chromosomes=True
    ):
        with open(loci_file_path, 'r') as loci_file:
            for line in loci_file:
                if not line.startswith(('#', 'track name')):
                    chr, start, end, locus_name = tuple(
                        column.strip('\'\"\n')
                        for column in ine.split()
                    )
                    if min_interval_size:
                        start = int(start)
                        end = int(end)
                        center = statistics.mean((start, end))
                        if ((start - end) < min_interval_size):
                            center = (start + end) / 2
                            start, end = tuple(
                                int(endpoint) for endpoint in (
                                    center - min_interval_size / 2,
                                    center + min_interval_size / 2
                                )
                            )
                    try:
                        self.chromosome[
                            casefold_chromosome_name(chr)
                        ].add_locus(
                            name=locus_name,
                            interval=(start, end)
                        )
                    except KeyError:
                        if add_chromosomes:
                            self.add_chromosome(chr)
                            self.chromosome[
                                casefold_chromosome_name(chr)
                            ].add_locus(
                                name=locus_name, interval=(start, end)
                            )
    
    def load_loci_from_variants(
        self,
        variants_file_path,
        add_header=None,
        replace_header=None,
        chromosome=None,
        position=None,
        id=None,
        locus=None,
        traits=None,
        trait=None,
        index_variants=False,
        min_interval_size=None,
        set_header=True,
        delimiter=None,
        add_chromosomes=True
    ):
        if index_variants and not min_interval_size:
            min_interval_size=1e6
        self.load_variants(
            variants_file_path,
            add_header=add_header,
            replace_header=replace_header,
            chromosome=chromosome,
            position=position,
            id=id,
            locus=locus,
            traits=traits,
            trait=trait,
            index_variants=index_variants,
            set_header=set_header,
            delimiter=delimiter,
            add_chromosomes=add_chromosomes
        )
        for chromosome in self.chromosomes:
            chromosome.sort_variants()
            variants_per_locus = {}
            for variant in chromosome.variants:
                if (
                    isinstance(variant, IndexVariant)
                    if index_variants else True
                ):
                    try:
                        variants_per_locus[variant.locus_name].append(variant)
                    except KeyError:
                        variants_per_locus[variant.locus_name] = [variant]
            for locus_name, variants in variants_per_locus.items():
                positions = tuple(
                    variant.position for variant in variants
                )
                center = statistics.mean(positions)
                interval = (
                    min(min(positions), int(center - min_interval_size / 2)),
                    max(max(positions), int(center + min_interval_size / 2))
                )
                if index_variants:
                    chromosome.add_locus(
                        name=locus_name,
                        interval=interval,
                        index_variants=variants,
                        variants=copy.copy(variants)
                    )
                else:
                    chromosome.add_locus(
                        name=locus_name, interval=interval, variants=variants
                    )

    def load_variants(
        self,
        variants_file_path,
        add_header=None,
        replace_header=None,
        chromosome=None,
        position=None,
        id=None,
        locus=None,
        index_variants=False,
        traits=None,
        trait=None,
        set_header=True,
        delimiter=None,
        add_chromosomes=True,
        exclude_hla=False,
        predicate=None,
        vcf=False
    ):
        with compression_agnostic_open(variants_file_path) as variants_file:
            if vcf:
                variants_file = itertools.dropwhile(
                    lambda line: line[:2] == '##', variants_file
                )
            variants_header = parse_variants_header(
                variants_file=variants_file,
                add_header=add_header,
                replace_header=replace_header,
                chromosome=chromosome,
                position=position,
                id=id,
                locus=locus,
                traits=traits,
                trait=trait,
                delimiter=delimiter,
                vcf=vcf
            )
            if set_header:
                self.variants_header = variants_header
            for variant in (
                (
                    IndexVariant(tup, variants_header) if index_variants
                    else Variant(tup, variants_header)
                )
                for tup in {
                    tuple(
                        line.rstrip('\n').split(
                            *((delimiter,) if delimiter else ())
                        )
                    )
                    for line in variants_file
                    if not line.startswith(('#', 'track name'))
                }
            ):
                try:
                    if (predicate(variant) if predicate else True) and any(
                        (
                            not exclude_hla,
                            variant.chromosome != '6',
                            variant.position > 35e6,
                            variant.position < 25e6
                        )
                    ):
                        self.chromosome[variant.chromosome].variants.append(
                            variant
                        )
                except KeyError:
                    if add_chromosomes:
                        self.add_chromosome(variant.chromosome)
                        self.chromosome[variant.chromosome].variants.append(
                            variant
                        )
    
    def load_eqtl_mapping_data(
        self,
        eqtl_mapping_file_path,
        *genes_and_variants,
        add_header=None,
        replace_header=None,
        chromosome=None,
        position=None,
        id=None,
        gene=None,
        summary_statistics=None,
        set_header=True,
        cell='cell',
        delimiter=None,
        add_chromosomes=True,
        add_loci=True
    ):
        genes, variant_coordinates = separate_genes_and_variants(
            genes_and_variants
        )
        with compression_agnostic_open(
            eqtl_mapping_file_path
        ) as eqtl_mapping_file:
            variants_header = parse_eqtl_mapping_header(
                eqtl_mapping_file=eqtl_mapping_file,
                add_header=add_header,
                replace_header=replace_header,
                chromosome=chromosome,
                position=position,
                id=id,
                gene=gene,
                summary_statistics=summary_statistics,
                delimiter=delimiter
            )
            if set_header:
                self.variants_header = variants_header
        eqtl_mapping_file_suffix = eqtl_mapping_file_path[-3:]
        if eqtl_mapping_file_suffix == '.gz':
            with tempfile.NamedTemporaryFile() as temp_mapping:
                temp_eqtl_mapping_file_path = temp_mapping.name
            with open(temp_eqtl_mapping_file_path, 'w') as temp_mapping:
                with subprocess.Popen(
                    ('zcat', eqtl_mapping_file_path),
                    stdout=subprocess.PIPE
                ) as zcat:
                    subprocess.call(
                        (
                            'awk',
                            (
                                'NR==1 || ' * (not add_header),
                                + ' || '.join(
                                    '${}=="{}"'.format(
                                        variants_header.gene_index + 1, gene
                                    )
                                    for gene in genes
                                )
                                +  ' || '
                                * bool(genes)
                                * bool(variant_coordinates)
                                + ' || '.join(
                                    '(${}=={} && ${}=={})'.format(
                                        variants_header.chromosome_index + 1,
                                        variant_coordinate[0],
                                        variants_header.position_index + 1,
                                        variant_coordinate[1],
                                    
                                    )
                                    for variant_coordinate
                                    in variant_coordinates
                                )
                            )
                        ),
                        stdin=zcat.stdout,
                        stdout=temp_mapping
                    )
            eqtl_mapping_file_path = temp_eqtl_mapping_file_path
        with compression_agnostic_open(
            eqtl_mapping_file_path
        ) as eqtl_mapping_file:
            if not add_header:
                eqtl_mapping_file.readline()
            for variant in (
                Variant(tup, variants_header) for tup in {
                    tuple(
                        line.rstrip('\n').split(
                            *((delimiter,) if delimiter else ())
                        )
                    )
                    for line in eqtl_mapping_file
                    if not line.startswith(('#', 'track name'))
                    if (
                        (
                            (
                                line.split()[variants_header.gene_index]
                                in genes if genes else False
                            )
                            or (
                                (
                                    line.split()[
                                        variants_header.chromosome_index
                                    ],
                                    int(
                                        line.split()[
                                            variants_header.position_index
                                        ]
                                    )
                                )
                                in variant_coordinates if variant_coordinates
                                else False
                            )
                        )
                        if genes_and_variants else True
                    )
                }
            ):
                for summary_statistic in (
                    variants_header.summary_statistics.keys()
                ):
                    try:
                        variant.traits[
                            '{}_{}_expr'.format(
                                cell,
                                variant.tuple[variants_header.gene_index]
                            )
                        ][
                            summary_statistic
                        ] = try_float(
                            variant.tuple[
                                variants_header.summary_statistics[
                                    summary_statistic
                                ]
                            ]
                        )
                    except KeyError:
                        variant.traits[
                            '{}_{}_expr'.format(
                                cell,
                                variant.tuple[variants_header.gene_index]
                            )
                        ] = {
                            summary_statistic: try_float(
                                variant.tuple[
                                    variants_header.summary_statistics[
                                        summary_statistic
                                    ]
                                ]
                            )
                        }
                try:
                    self.chromosome[variant.chromosome].variants.append(
                        variant
                    )
                except KeyError:
                    if add_chromosomes:
                        self.add_chromosome(variant.chromosome)
                        self.chromosome[variant.chromosome].variants.append(
                            variant
                        )
        if eqtl_mapping_file_suffix == '.gz':
            os.remove(temp_eqtl_mapping_file_path)
        if add_loci:
            for chromosome in self.chromosomes:
                chromosome.sort_variants()
                variants_per_locus = {}
                for v in chromosome.variants:
                    try:
                        variants_per_locus[
                            v.tuple[variants_header.gene_index]
                        ].append(v)
                    except KeyError:
                        variants_per_locus[
                            v.tuple[variants_header.gene_index]
                        ] = [v]
                for locus_name, variants in variants_per_locus.items():
                    positions = tuple(v.position for v in variants)
                    interval = (min(positions), max(positions))
                    chromosome.add_locus(
                        name=locus_name,
                        interval=interval,
                        variants=variants
                    )
    
    def check_for_eqtls(
        self,
        variants,
        cells,
        false_discovery_rate=0.1
    ):
        variant_gene_pairs = (
            (variant, trait)
            for variant in variants
            for trait in variant.traits.keys()
            if any(
                (trait.startswith(cell + '_') and trait.endswith('_expr'))
                for cell in cells
            )
        )
        return eqtl_benjamini_hochberg(
            variant_gene_pairs,
            false_discovery_rate
        )
        
    
    def load_annotations(self, annotations_file_path, verbose=False):
        missing_chromosome_warnings = set()
        with open(annotations_file_path, 'r') as annotations_file:
            for chr, start, end, annotation_name in {
                tuple(line.rstrip('\n').split())
                for line in annotations_file
            }:
                start = int(start)
                end = int(end)
                try:
                    (
                        self.chromosome[casefold_chromosome_name(chr)]
                        .annotations[annotation_name]
                        .append((start, end))
                    )
                except KeyError:
                    try:
                        (
                            self.chromosome[casefold_chromosome_name(chr)]
                            .annotations[annotation_name]
                        ) = [(start, end)]
                    except KeyError:
                        missing_chromosome_warnings.add(
                            casefold_chromosome_name(chr)
                        )
                except (ValueError, IndexError):
                    raise Exception(
                        (
                            'Error: The annotation file does not appear to be '
                            'in headerless BED format at a line with the '
                            'following tuple representation:\n{}'
                        ).format(repr(annotation))
                    )
        if missing_chromosome_warnings and verbose:
            print(
                'Warning: chromosomes {} are not present on this genome, so '
                'annotations located there were ignored.'
                .format(', '.join(sorted(missing_chromosome_warnings)))
            )
    
    def sort_loci(self):
        for chromosome in self.chromosomes:
            chromosome.sort_loci()
    
    def resolve_overlapping_loci(self):
        for chromosome in self.chromosomes:
            chromosome.resolve_overlapping_loci()
    
    def get_locus(self, locus_name):
        for chromsome in self.chromosomes:
            for locus in chromosome.loci:
                if locus.name == locus_name:
                    return locus
    
    def sort_variants(self):
        for chromosome in self.chromosomes:
            chromosome.sort_variants()
    
    def check_variants_have_been_sorted(self):
        for chromosome in self.chromosomes:
            if not chromosome.variants_have_been_sorted:
                raise Exception(
                    'variants must be sorted before loci can be populated'
                )
    
    def resolve_duplicate_variants(
        self,
        trait=None,
        stat=None,
        preserve_index_variants=True,
        processes=None
    ):
        if not processes:
            processes = self.processes
        if processes > 1:
            print(
                'WARNING: In parallel mode, '
                'Genome.resolve_duplicate_variants() will remove duplicates '
                'but will not resolve traits. Use serial mode when handling '
                'multiple traits.'
            )
            for chromosome in self.chromosomes:
                if not chromosome.variants_have_been_sorted:
                    raise Exception(
                        'Variants on chromosome {} must be sorted '
                        'before duplicates can be resolved'
                        .format(chromosome.char)
                    )
            else:
                args_generator = itertools.chain(
                    (
                        (
                            chromosome.variants,
                            'chromosome {}'.format(chromosome.char),
                            trait,
                            stat,
                            preserve_index_variants
                        )
                        for chromosome in self.chromosomes
                    ),
                    (
                        (
                            locus.variants,
                            'locus {}'.format(locus.name),
                            trait,
                            stat,
                            preserve_index_variants
                        )
                        for chromosome in self.chromosomes
                        for locus in chromosome.loci
                    )
                )
                with Pool(processes=processes) as pool:
                    for chromosome_or_locus, variants in zip(
                        itertools.chain(
                            self.chromosomes,
                            (
                                locus
                                for chromosome in self.chromosomes
                                for locus in chromosome.loci
                            )
                        ),
                        pool.starmap(
                            resolve_and_report_duplicate_variants,
                            args_generator
                        )
                    
                    ):
                        chromosome_or_locus.variants = variants
        else:
            for chromosome in self.chromosomes:
                chromosome.resolve_duplicate_variants(
                    trait,
                    stat,
                    preserve_index_variants=preserve_index_variants
                )
    
    def populate_loci(
        self,
        ld_threshold=None,
        population=None,
        processes=None
    ):
        if not processes:
            processes = self.processes
        self.check_variants_have_been_sorted()
        if not ld_threshold:
            for chromosome in self.chromosomes:
                chromosome.populate_loci()
        elif ld_threshold:
            loci = tuple(
                locus
                for chromosome in self.chromosomes
                for locus in chromosome.loci
            )
            args_generator = (
                (
                    locus.chromosome.char,
                    locus.interval,
                    {
                        index_variant.position
                        for index_variant in locus.index_variants
                    },
                    ld_threshold,
                    population
                )
                for locus in loci
            )
            with Pool(processes=processes) as pool:
                for locus, positions_to_add in zip(
                    loci, pool.starmap(get_positions_in_ld, args_generator)
                ):
                    for variant in locus.chromosome.variants:
                        if variant.position in positions_to_add:
                            locus.variants.append(variant)
                    locus.sort_variants()
    
    def project_loci(
        self,
        genome,
        *locus_names,
        populate=True,
        ld_threshold=None,
        population=None,
        positions=None
    ):
        available_locus_names = {
            locus.name
            for chromosome in self.chromosomes
            for locus in chromosome.loci
        }
        if locus_names:
            if set(locus_names) - available_locus_names:
                raise Exception(
                    'Some of the indicated loci are not present on this genome'
                )
        else:
            locus_names = available_locus_names
        try:
            for chromosome in self.chromosomes:
                for locus in chromosome.loci:
                    if locus.name in locus_names:
                        locus.project(
                            genome.chromosome[chromosome.char],
                            populate=populate,
                            ld_threshold=ld_threshold,
                            population=population,
                            positions=positions
                        )
        except KeyError:
            raise Exception(
                'Target genome has no chromosome {}'.format(chromosome.char)
            )
    
    def restrict_to_loci(self):
        for chromosome in self.chromosomes:
            chromosome.restrict_to_loci()
    
    def restrict_to_outside_loci(self):
        for chromosome in self.chromosomes:
            chromosome.restrict_to_outside_loci()
    
    def get_variant(self, arg):
        if isinstance(arg, str):
            for chromosome in self.chromosomes:
                for variant in chromosome.variants:
                    if variant.id == arg:
                        return variant
        elif isinstance(arg, tuple):
            for variant in self.chromosome[arg[0]].variants:
                if variant.position == arg[1]:
                    return variant
    
    def sort_annotations(self):
        for chromosome in self.chromosomes:
            chromosome.sort_annotations()
    
    def annotate_variants(
        self,
        annotation_subset=None,
        processes=None
    ):
        if not processes:
            processes = self.processes
        if processes > 1:
            for chromosome in self.chromosomes:
                if not (
                    chromosome.variants_have_been_sorted
                    and chromosome.annotations_have_been_sorted
                ):
                    raise Exception(
                        'Variants and annotations on chromosome {} must be sorted '
                        'before variants can be annotated'
                        .format(chromosome.char)
                    )
            else:
                zip_positions_annotations = tuple(
                    (
                        tuple(
                            variant.position for variant in chromosome.variants
                        ),
                        chromosome.annotations,
                        annotation_subset
                    )
                    for chromosome in self.chromosomes
                )
                with Pool(processes=processes) as pool:
                    for chromosome, annotations_per_variant in zip(
                        self.chromosomes,
                        pool.starmap(
                            annotate_variants,
                            zip_positions_annotations
                        )
                    ):
                        for variant, annotations in zip(
                            chromosome.variants,
                            annotations_per_variant
                        ):
                            variant.annotations = (
                                variant.annotations | annotations
                            )
        else:
            for chromosome in self.chromosomes:
                chromosome.annotate_variants()
    
    def compute_zsq_from_pval(self, trait):
        for chromosome in self.chromosomes:
            chromosome.compute_zsq_from_pval(trait)
    
    def compute_z_from_beta_se(self, *traits):
        for chromosome in self.chromosomes:
            chromosome.compute_z_from_beta_se(*traits)
    
    def compute_lnbfs(
        self,
        *traits,
        sample_size=None,
        cases=None,
        controls=None,
        prior_variance=None
    ):
        for chromosome in self.chromosomes:
            chromosome.compute_lnbfs(
                *traits,
                sample_size=sample_size,
                cases=cases,
                controls=controls,
                prior_variance=prior_variance
            )
    
    def probability_mass_explained(self, trait, *annotations):
        loci = tuple(
            locus
            for chromosome in self.chromosomes
            for locus in chromosome.loci
        )
        return (
            sum(
                locus.probability_mass_explained(trait, *annotations)
                for locus in loci
            )
            / len(loci)
        )
    
    def collect_mafs(
        self,
        *traits,
        population='ALL',
        processes=None,
        dictionary=None
    ):
        if not processes:
            processes = self.processes
        traits = set(traits)
        variants = tuple(
            variant
            for chromosome in self.chromosomes
            for variant in chromosome.variants
            if set(variant.traits.keys()) & traits
        )
        if dictionary:
            for variant in variants:
                for trait in traits:
                    if variant.traits.get(trait):
                        if not variant.traits[trait].get('maf'):
                            variant.traits[trait]['maf'] = dictionary.get(
                                variant.id
                            )
                            if not variant.traits[trait].get('maf'):
                                print(
                                    'Warning: MAF could not be collected for '
                                    '{}'
                                    .format(variant)
                                )
        else:
            coordinate_generator = (
                (variant.chromosome, variant.position, population)
                for variant in variants
            )
            with Pool(processes=processes) as pool:
                for maf, variant in zip(
                    pool.starmap(
                        py1kgp.fast_maf,
                        coordinate_generator
                    ),
                    variants
                ):
                    for trait in traits:
                        if variant.traits.get(trait):
                            if not variant.traits[trait].get('maf'):
                                variant.traits[trait]['maf'] = try_float(maf)
                                if not variant.traits[trait].get('maf'):
                                    print(
                                        'Warning: MAF could not be collected '
                                        'for {}'
                                        .format(variant)
                                    )
    
    def intersect_traits(self, *args, verbose=False):
        for chromosome in self.chromosomes:
            chromosome.intersect_traits(*args, verbose=verbose)
    
    def format(self, header):
        if not isinstance(header, VariantsHeader):
            header = VariantsHeader(header)
        for chromosome in self.chromosomes:
            chromosome.format(header)
    
    def import_snp_snap_matched_variants(self, variants, snp_snap_matches_file):
        matched_variant_coordinates = {
            chromosome.char: []
            for chromosome in self.chromosomes
        }
        test_coordinates = {
            (variant.chromosome, variant.position) for variant in variants
        }
        chromosomes_not_in_genome = set()
        matched_variants = set()
        with open(snp_snap_matches_file, 'r') as matches_file:
            matches_file.readline()
            for chr, position in (
                coordinate.split(':')
                for line in matches_file
                for coordinate in line.split()[1:]
            ):
                try:
                    matched_variant_coordinates[chr].append(int(position))
                except KeyError:
                    chromosomes_not_in_genome.add(chr)
        if chromosomes_not_in_genome:
            print(
                'Warning: chromosomes {} were indicated in the matches file '
                'but are not present in this genome'
                .format(', '.join(sorted(chromosomes_not_in_genome)))
            )
        for chr, positions in matched_variant_coordinates.items():
            positions.sort()
            for variant in self.chromosome[chr].variants:
                checked_positions = set()
                for position in positions:
                    if variant.position > position:
                        checked_positions.add(position)
                    elif variant.position == position:
                        if not (
                            (variant.chromosome, variant.position)
                            in test_coordinates
                        ):
                            matched_variants.add(variant)
                        checked_positions.add(position)
                        break
                    elif variant.position < position:
                        break
                if checked_positions:
                    for position in checked_positions:
                        positions.remove(position)
        return matched_variants
    
    def test_enrichment(
        self,
        variants,
        trait,
        snp_snap_matches_file,
        pval=None,
        lnbf=None
    ):
        self.check_variants_have_been_sorted()
        matched_variants = self.import_matched_variants(
            variants,
            snp_snap_matches_file
        )
        if pval:
            matched_pvals = tuple(
                variant.traits[trait]['pval'] for variant in matched_variants
            )
            test_pvals = tuple(
                variant.traits[trait]['pval'] for variant in variants
            )
            table = (
                (
                    len(tuple(val for val in test_pvals if val <= pval)),
                    len(tuple(val for val in matched_pvals if val <= pval))
                ),
                (
                    len(tuple(val for val in test_pvals if val > pval)),
                    len(tuple(val for val in matched_pvals if val > pval))
                )
            )
            return {
                'table': table,
                'fisher_exact': scipy.stats.fisher_exact(
                    table,
                    alternative='greater'
                )
            }
        elif lnbf:
            matched_lnbfs = tuple(
                variant.traits[trait]['lnbf'] for variant in matched_variants
            )
            test_lnbfs = tuple(
                variant.traits[trait]['lnbf'] for variant in variants
            )
            table = (
                (
                    len(tuple(val for val in test_lnbfs if val >= lnbf)),
                    len(tuple(val for val in matched_lnbfs if val >= lnbf))
                ),
                (
                    len(tuple(val for val in test_lnbfs if val < lnbf)),
                    len(tuple(val for val in matched_lnbfs if val < lnbf))
                )
            )
            return {
                'table': table,
                'fisher_exact':
                    scipy.stats.fisher_exact(table, alternative='greater')
            }
    
    def export_variants(
        self,
        file_path,
        variants_header,
        delimiter='\t',
        compress=False
    ):
        header = variants_header.tuple
        variants = (
            variant.tuple
            for chromosome in self.chromosomes
            for variant in chromosome.variants
        )
        with (
            gzip.open(file_path, 'wb') if compress else open(file_path, 'wb')
        ) as f:
            f.write(
                '\n'.join(
                    delimiter.join(row)
                    for row in itertools.chain((header,), variants, ('',))
                )
                .encode()
            )
    
    def export_loci(
        self,
        file_path,
        variants_header,
        delimiter='\t',
        compress=False
    ):
        header = (
           variants_header.tuple
           + bool(not hasattr(variants_header, 'locus_index')) * ('locus',)
        )
        variants = tuple(
            (
                variant.tuple
                + bool(not hasattr(variants_header, 'locus_index'))
                * (locus.name,)
            )
            for chromosome in self.chromosomes
            for locus in chromosome.loci
            for variant in locus.variants
        )
        with (
            gzip.open(file_path, 'wb') if compress else open(file_path, 'wb')
        ) as f:
            f.write(
                '\n'.join(
                    delimiter.join(row)
                    for row in ((header,) + variants + ('',))
                )
                .encode()
            )
        
    def export_vam(
        self,
        file_path,
        variants_header,
        delimiter='\t',
        compress=False
    ):
        annotations = tuple(
            sorted(
                {
                    annotation_name
                    for chromosome in self.chromosomes
                    for annotation_name in chromosome.annotations.keys()
                }
            )
        )
        header = variants_header.tuple + annotations
        matrix = (
            (
                variant.tuple
                + tuple(
                    str(int(annotation in variant.annotations))
                    for annotation in annotations
                )
            )
            for chromosome in self.chromosomes
            for variant in chromosome.variants
        )
        with (
            gzip.open(file_path, 'wb') if compress else open(file_path, 'wb')
        ) as f:
            f.write(
                '\n'.join(
                    delimiter.join(row)
                    for row in itertools.chain((header,), matrix, ('',))
                )
                .encode()
            )
    
    def export_fgwas_input(
        self,
        file_path,
        trait,
        population=None,
        sample_size=None,
        cases=None,
        controls=None,
        lnbf=False,
        fine_mapping=False
    ):
        if fine_mapping:
            for segnumber, locus in enumerate(
                locus
                for chromosome in self.chromosomes
                for locus in chromosome.loci
            ):
                locus.segnumber = segnumber
                for variant in locus.variants:
                    variant.segnumber = segnumber
        annotations = tuple(
            sorted(
                {
                    annotation_name
                    for chromosome in self.chromosomes
                    for annotation_name in chromosome.annotations.keys()
                }
            )
        )
        header = (
            ('SNPID', 'CHR', 'POS', 'Z', 'F')
            + ('N',) * (bool(sample_size) if not lnbf else True)
            + ('NCASE', 'NCONTROL') * bool(cases) * bool(controls)
            + ('LNBF',) * lnbf
            + ('SEGNUMBER',) * fine_mapping
            + annotations
        )
        matrix = (
            (
                variant.id,
                variant.chromosome,
                variant.position,
                (
                    math.sqrt(
                        variant.traits[trait].get(
                            'zsq', variant.compute_zsq_from_pval(trait)
                        )
                    )
                    if not lnbf else '.'
                ),
                (variant.traits[trait]['maf'] if not lnbf else '.')
            )
            + (((sample_size,) * bool(sample_size)) if not lnbf else ('.',))
            + (cases, controls) * bool(cases) * bool(controls)
            + (variant.traits[trait].get('lnbf'),) * lnbf
            + ((getattr(variant, 'segnumber', None),) * fine_mapping)
            + tuple(
                int(annotation in variant.annotations)
                for annotation in annotations
            )
            for chromosome in self.chromosomes
            for variant in chromosome.variants
            if variant.traits.get(trait)
            if variant.traits[trait].get('maf', lnbf)
        )
        if fine_mapping:
            segnumber_index = header.index('SEGNUMBER')
            matrix = tuple(
                sorted(matrix, key=lambda row: int(row[segnumber_index]))
            )
        with gzip.open(
            '{}.gz'.format(file_path.replace('.gz', '')),
            'wb'
        ) as f:
            f.write(
                '\n'.join(
                    ' '.join(str(col) for col in row)
                    for row in itertools.chain((header,), matrix, ('',))
                )
                .encode()
            )


@bootstrap
class Chromosome():
    '''A chromosome'''
    
    @classmethod
    def bootstrap(cls):
        for comparison_string in (
            '__eq__',
            '__ne__',
            '__lt__',
            '__le__',
            '__gt__',
            '__ge__'
        ):
            integer_comparison = getattr(int, comparison_string)
            def chromosome_comparison(
                self, chr, integer_comparison=integer_comparison
            ):
                return integer_comparison(self.int, chr.int)
            setattr(cls, comparison_string, chromosome_comparison)
    
    def __init__(self, chromosome_name):
        self.char = casefold_chromosome_name(chromosome_name)
        try:
            self.int = int(self.char)
            if self.int not in range(1,26):
                self.raise_chromosome_name_error(chromosome_name)
        except ValueError:
            try:
                self.int = {'X': 23, 'Y': 24, 'M': 25, 'MT': 25}[self.char]
            except KeyError:
                self.raise_chromosome_name_error(chromosome_name)
        self.locus = {}
        self.loci = []
        self.variants = []
        self.annotations = {}
        self.loci_have_been_sorted = False
        self.variants_have_been_sorted = False
        self.annotations_have_been_sorted = False
    
    def __int__(self):
        return self.int
    
    def __repr__(self):
        return 'Chromosome({}, loci: {}, variants: {})'.format(
            self.char,
            [locus.name for locus in self.loci],
            len(self.variants)
        )
    
    def __len__(self):
        return len(self.variants)
    
    # Locus operations
    
    def add_locus(self, name, interval=None, index_variants=[], variants=[]):
        locus = Locus(
            name=name,
            chromosome=self,
            interval=interval,
            index_variants=index_variants,
            variants=variants
        )
        self.locus[locus.name] = locus
        self.loci.append(locus)
    
    def sort_loci(self):
        self.loci.sort()
        self.loci_have_been_sorted = True
    
    def resolve_overlapping_loci(self):
        if self.loci_have_been_sorted:
            merge_sets = []
            for locus in self.loci:
                if locus not in tuple(
                    loc for merge_set in merge_sets for loc in merge_set
                ):
                    if (
                        tuple(loc.interval for loc in self.loci)
                        .count(locus.interval)
                        > 1
                    ):
                        merge_sets.append(
                            tuple(
                               loc for loc in self.loci if (
                                   loc.interval == locus.interval
                                )
                            )
                        )
            for merge_set in merge_sets:
                merged_locus = Locus(
                    (
                        self.char,
                        merge_set[0].interval[0],
                        merge_set[0].interval[1],
                        ','.join(locus.name for locus in merge_set)
                    )
                )
                merged_locus.positions_allowed = (
                    set().union(
                        *tuple(locus.positions_allowed for locus in merge_set)
                    )
                )
                for locus in merge_set:
                    self.loci.remove(locus)
                    print('removed', locus.name)
                self.loci.append(merged_locus)
                print('appended', merged_locus.name)
            self.sort_loci()
            for index in range(len(self.loci) - 1):
                if (
                    self.loci[index].interval[1]
                    >= self.loci[index + 1].interval[0]
                ):
                    if (
                        self.loci[index].interval[1]
                        >= self.loci[index + 1].interval[1]
                    ):
                        if (
                            (
                                self.loci[index + 1].interval[0]
                                - self.loci[index].interval[0]
                            )
                            >= (
                                self.loci[index].interval[1]
                                - self.loci[index + 1].interval[1]
                            )
                        ):
                            self.loci[index].interval = (
                                self.loci[index].interval[0],
                                self.loci[index + 1].interval[0] - 1
                            )
                        else:
                            self.loci[index].interval = (
                                self.loci[index + 1].interval[1] + 1,
                                self.loci[index].interval[1]
                            )
                    else:
                        critical_point = int(
                            statistics.mean(
                                (
                                    self.loci[index].interval[1],
                                    self.loci[index + 1].interval[0]
                                )
                            )
                        )
                        self.loci[index].interval = (
                            self.loci[index].interval[0], critical_point - 1
                        )
                        self.loci[index + 1].interval = (
                            critical_point, self.loci[index + 1].interval[1]
                        )
        else:
            raise Exception(
                'Loci must be sorted before overlaps can be resolved'
            )
    
    def populate_loci(
        self,
        ld_threshold=None,
        population=None,
        processes=1
    ):
        if not self.variants_have_been_sorted:
            raise Exception(
                'variants must be sorted before loci can be populated'
            )
        elif not ld_threshold:
            for locus in self.loci:
                locus.populate()
        elif ld_threshold:
            args_generator = (
                (
                    self.char,
                    locus.interval,
                    {
                        index_variant.position
                        for index_variant in locus.index_variants
                    },
                    ld_threshold,
                    population
                )
                for locus in self.loci
            )
            with Pool(processes=processes) as pool:
                positions_in_ld = pool.starmap(
                    get_positions_in_ld, args_generator
                )
            for locus, positions_to_add in zip(self.loci, positions_in_ld):
                for variant in self.variants:
                    if variant.position in positions_to_add:
                        locus.variants.append(variant)
                locus.sort_variants()
    
    def project_loci(
        self,
        chromosome,
        *locus_names,
        populate=True,
        ld_threshold=None,
        population=None,
        positions=None
    ):
        try:
            for locus in (
                (self.locus[locus_name] for locus_name in locus_names)
                if locus_names else self.loci
            ):
                locus.project(
                    chromosome,
                    populate=populate,
                    ld_threshold=ld_threshold,
                    population=population,
                    positions=positions
                )
        except KeyError:
            raise Exception(
                'Chromosome {} has no locus {}!'
                .format(self.chromosome.char, self.name)
            )
    
    # Variant operations
    
    def sort_variants(self):
        self.variants.sort(key=operator.attrgetter('position'))
        for locus in self.loci:
            locus.sort_variants()
        self.variants_have_been_sorted = True
    
    def resolve_duplicate_variants(
        self,
        trait,
        stat,
        preserve_index_variants=True
    ):
        if self.variants_have_been_sorted:
            self.variants = resolve_and_report_duplicate_variants(
                self.variants,
                'chromosome {}'.format(self.char),
                trait,
                stat,
                preserve_index_variants=preserve_index_variants
            )
            for locus in self.loci:
                locus.resolve_duplicate_variants(
                    trait,
                    stat,
                    preserve_index_variants=preserve_index_variants
                )
        else:
            raise Exception(
                'Variants must be sorted before duplicates can be removed'
            )
    
    def restrict_to_loci(self):
        self.variants = [
            variant for locus in self.loci for variant in locus.variants
        ]
    
    def restrict_to_outside_loci(self):
        locus_variants = {
            variant for locus in self.loci for variant in locus.variants
        }
        self.variants = [
            variant for variant in self.variants
            if (variant not in locus_variants)
        ]
        for locus in self.loci:
            locus.variants = []
    
    def get_variant(self, arg):
        if isinstance(arg, str):
            for variant in self.variants:
                if variant.id == arg:
                    return variant
        elif isinstance(arg, tuple):
            for variant in self.variants:
                if variant.position == arg[1]:
                    return variant
        elif isinstance(arg, int):
            for variant in self.variants:
                if variant.position == arg:
                    return variant
    
    def look_up_rsids(self, processes=1):
        with Pool(processes=processes) as pool:
            for variant, rsid in zip(
                self.variants,
                pool.starmap(
                    look_up_rsid, ((variant, True) for variant in self.variants)
                )
            ):
                variant.id = rsid
    
    def compute_zsq_from_pval(self, trait):
        for variant in self.variants:
            variant.compute_zsq_from_pval(trait)
    
    def compute_z_from_beta_se(self, *traits):
        for variant in self.variants:
            variant.compute_z_from_beta_se(*traits)
    
    def compute_lnbfs(
        self,
        *traits,
        sample_size=None,
        cases=None,
        controls=None,
        prior_variance=None
    ):
        for variant in self.variants:
            variant.compute_lnbf(
                *traits,
                sample_size=sample_size,
                cases=cases,
                controls=controls,
                prior_variance=prior_variance
            )
    
    def intersect_traits(self, *args, verbose=False):
        intersect_traits(self, *args)
        if verbose:
            print(
                '{} variants were in the intersection of {} on chromosome {}'
                .format(len(self.variants), sorted(args), self.char)
            )
        for locus in self.loci:
            locus.intersect_traits(*args, verbose=verbose)
    
    def format(self, header):
        if not isinstance(header, VariantsHeader):
            header = VariantsHeader(header)
        for variant in self.variants:
            variant.format(header)
    
    # Annotation operations
    
    def sort_annotations(self):
        for name, interval_list in self.annotations.items():
            interval_list.sort()
        self.annotations_have_been_sorted = True
    
    def annotate_variants(self, annotation_subset=None):
        if (
            self.variants_have_been_sorte and self.annotations_have_been_sorted
        ):
            annotations_per_variant = annotate_variants(
                variant_positions=tuple(
                    variant.position for variant in self.variants
                ),
                annotations=self.annotations,
                annotation_subset=annotation_subset
            )
            for variant, annotations in zip(
                self.variants, annotations_per_variant
            ):
                variant.annotations = variant.annotations | annotations
        else:
            raise Exception(
                'Variants and annotations must be sorted before variants can '
                'be annotated'
            )
                
    def raise_chromosome_name_error(self, chromosome_name):
        raise Exception(
            'Error: {} is not a valid chromosome name. Valid names include '
            'integers 1-25 or characters XxYyMm and may or not be prefixed '
            'with chr, CHR, Chr, etc.'.format(str(chromosome_name))
        )


@bootstrap
class Locus():
    """A locus"""
    
    @classmethod
    def bootstrap(cls):
        for comparison_string in (
            '__eq__',
            '__ne__',
            '__lt__',
            '__le__',
            '__gt__',
            '__ge__'
        ):
            interval_comparison = getattr(tuple, comparison_string)
            def locus_comparison(
                self, loc, interval_comparison=interval_comparison
            ):
                return interval_comparison(self.interval, loc.interval)
            setattr(cls, comparison_string, locus_comparison)
    
    def __init__(
        self,
        name,
        chromosome,
        interval=None,
        index_variants=[], 
        variants=[]
    ):
        if not (interval or variants):
            raise BadArgumentError(
                'Either an interval or a list of variants must be specified.'
            )
        self.name = name
        self.chromosome = chromosome
        self.interval = (
            tuple(int(endpoint) for endpoint in interval) if interval
            else (
                min(variant.position for variant in index_variants + variants),
                max(variant.position for variant in index_variants + variants)
            )
        )
        self.index_variants = index_variants
        self.variants = variants
        self.segnumber = None
        self.variants_have_been_sorted = False
    
    def __repr__(self):
        return (
            'Locus({}, chr={}, interval={}, index_variants={}, variants: {})'
            .format(
                self.name,
                self.chromosome.char,
                self.interval,
                self.index_variants,
                len(self.variants)
            )
        )
    
    def __len__(self):
        return len(self.variants)
    
    def populate(
        self,
        ld_threshold=None,
        population=None,
        positions=None
    ):
        positions_already_added = {
            variant.position
            for locus in self.chromosome.loci
            for variant in locus.variants
        }
        if ld_threshold:
            positions_in_ld = get_positions_ld(
                chromosome=self.chromosome.char,
                interval=self.interval,
                index_positions={
                    index_variant.position
                    for index_variant in self.index_variants
                },
                ld_threshold=ld_threshold,
                population=population
            )
            positions = ( 
                (
                    positions_in_ld & set(positions)
                    if positions else positions_in_ld
                )
                - positions_already_added
            )
            for variant in self.chromosome.variants:
                if variant.position in positions:
                    self.variants.append(variant)
            self.sort_variants()
        elif positions:
            positions = set(positions) - positions_already_added
            for variant in self.chromosome.variants:
                if variant.position in positions:
                    self.variants.append(variant)
        else:
            for variant in self.chromosome.variants:
                if (
                    variant.position >= self.interval[0]
                    and variant.position <= self.interval[1]
                ):
                    if variant.position not in positions_already_added:
                        self.variants.append(variant)
                elif variant.position > self.interval[1]:
                    break
            self.sort_variants()
        for variant in self.variants:
            variant.locus_name = self.name
    
    def project(
        self,
        chromosome,
        populate=True,
        ld_threshold=None,
        population=None,
        positions=None
    ):
        if self.chromosome.char != chromosome.char:
            raise Exception(
                'Can\'t project locus {} to chromosome {}!'
                .format(self.name, chromosome.char)
            )
        if chromosome.locus.get(self.name):
            chromosome.locus[self.name].interval = (
                min(self.interval[0], chromosome.locus[self.name].interval[0]),
                max(self.interval[1], chromosome.locus[self.name].interval[1])
            )
            chromosome.locus[self.name].index_variants = sorted(
                (
                    {
                        variant for variant in chromosome.variants
                        if variant.position in {
                            index_variant.position
                            for index_variant in self.index_variants
                        }
                    }
                    | set(chromosome.locus[self.name].index_variants)
                ),
                key=operator.attrgetter('position')
            )
        else:
            chromosome.add_locus(
                name=self.name,
                interval=self.interval,
                index_variants = (
                    [
                        variant for variant in chromosome.variants
                        if variant.position in {
                            index_variant.position
                            for index_variant in self.index_variants
                        }
                    ]
                    if populate else []
                )
            )
        if populate:
            chromosome.locus[self.name].populate(
                ld_threshold=ld_threshold,
                population=population,
                positions=positions
            )
    
    def sort_variants(self):
        self.variants.sort(key=operator.attrgetter('position'))
        self.variants_have_been_sorted = True
        
    def resolve_duplicate_variants(
        self,
        trait,
        stat,
        preserve_index_variants=True
    ):
        if self.variants_have_been_sorted:
            self.variants = resolve_and_report_duplicate_variants(
                self.variants,
                'locus {}'.format(self.name),
                trait,
                stat,
                preserve_index_variants=preserve_index_variants
            )
            chromosome_variants_set = set(self.chromosome.variants)
            self.variants = [
                variant for variant in self.variants
                if variant in chromosome_variants_set
            ]
        else:
            raise Exception(
                'Variants must be sorted before duplicates can be removed'
            )
    
    def get_variant(self, arg):
        if isinstance(arg, str):
            for variant in self.variants:
                if variant.id == arg:
                    return variant
        elif isinstance(arg, tuple):
            for variant in self.variants:
                if variant.position == arg[1]:
                    return variant
        elif isinstance(arg, int):
            for variant in self.variants:
                if variant.position == arg:
                    return variant
    
    def density(self):
        return len(self.variants) / (self.interval[1] - self.interval[0])
    
    def min_pvalue(self, trait):
        return min(
            variant.traits[trait]['pval'] for variant in self.variants
        )
    
    def max_lnbf(self, trait):
        return max(
            variant.traits[trait]['lnbf'] for variant in self.variants
        )
    
    def intersect_traits(self, *args, verbose=False):
        intersect_traits(self, *args)
        if verbose:
            print(
                '{} variants were in the intersection of {} at {}'
                .format(len(self.variants), sorted(args), self.name)
            )
    
    def format(self, header):
        if not isinstance(header, VariantsHeader):
            header = VariantsHeader(header)
        for variant in self.variants:
            variant.format(header)
    
    def compute_z_from_beta_se(self, *traits):
        for variant in self.variants:
            variant.compute_z_from_beta_se(*traits)
    
    def compute_lnbfs(
        self,
        *traits,
        sample_size=None,
        cases=None,
        controls=None,
        prior_variance=None
    ):
        for variant in self.variants:
            variant.compute_lnbf(
                *traits,
                sample_size=sample_size,
                cases=cases,
                controls=controls,
                prior_variance=prior_variance
            )
    
    def credible_set(self, trait, probability_mass=0.95):
        sorted_lnbf_variant_pairs = sorted(
            (
                (variant.traits[trait]['lnbf'], variant)
                for variant in self.variants if variant.traits.get(trait) if (
                    variant.traits[trait].get('lnbf')
                    or variant.traits[trait].get('lnbf') == 0
                )
            ),
            key=operator.itemgetter(0),
            reverse=True
        )
        ln_normalizing_constant = sumstats.log_sum(
            lnbf for lnbf, variant in sorted_lnbf_variant_pairs
        )
        running_probability_mass = 0
        credible_set = set()
        for ppa, variant in (
            (math.exp(lnbf - ln_normalizing_constant), variant)
            for lnbf, variant in sorted_lnbf_variant_pairs
        ):
            variant.traits[trait]['ppa'] = ppa
            credible_set.add(variant)
            running_probability_mass += ppa
            if running_probability_mass >= probability_mass:
                return credible_set
        else:
            return credible_set
    
    def coloc(
        self,
        trait1,
        trait2,
        prior1=1e-4,
        prior2=1e-4,
        prior12=1e-5
    ):
        trait1_lnbfs, trait2_lnbfs = self.collect_lnbfs_for_coloc(
            trait1,
            trait2
        )
        return coloc.coloc(
            trait1_lnbfs,
            trait2_lnbfs,
            prior1=prior1,
            prior2=prior2,
            prior12=prior12
        )
    
    def collect_lnbfs_for_coloc(self, trait1, trait2, handle_nans=False):
        return zip(
            *(
                (v.traits[trait1]['lnbf'], v.traits[trait2]['lnbf'])
                for v in self.variants
                if v.traits.get(trait1) and v.traits.get(trait2)
                if v.traits[trait1].get('lnbf') and v.traits[trait2].get('lnbf')
                if (not handle_nans) or not any(
                    (
                        math.isnan(v.traits[trait1]['lnbf']),
                        math.isnan(v.traits[trait2]['lnbf'])
                    )
                )
            )
        )
    
    def combined_evidence(self, *traits):
        return (
            (variant, sum(variant.traits[trait]['lnbf'] for trait in traits))
            for variant in self.variants
            if set(traits) <= set(variant.traits.keys())
        )
    
    def export_plotting_data(self, file_path, *traits, combined_evidence=False):
        variants = tuple(
            variant for variant in self.variants
            if set(variant.traits.keys()) & set(traits)
        )
        plotting_data = {
            'chr': [variant.chromosome for variant in variants],
            'pos': [variant.position for variant in variants],
            'id': [variant.id for variant in variants]
        }
        for trait in traits:
            plotting_data[trait] = [
                (
                    variant.traits[trait].get('lnbf')
                    if variant.traits.get(trait) else None
                )
                for variant in variants
            ]
        if combined_evidence:
            plotting_data['combined_evidence'] = [
                lnbf for variant, lnbf in self.combined_evidence(*traits)
            ]
        with open(file_path, 'w') as f:
            json.dump(plotting_data, f)
    
    def linkage(self, variant):
        position_to_variant_dict = {
            variant.position: variant for variant in self.variants
        }
        if isinstance(variant, tuple):
            chr, pos = variant
        elif isinstance(variant, str):
            if RSID_REGEX.match(variant):
                chr, pos = pyhg19.coord_tuple(variant)
        elif isinstance(variant, Variant):
            pos = variant.position
        with tempfile.NamedTemporaryFile() as (
            temp_vcf
        ), tempfile.NamedTemporaryFile() as (
            temp_positions
        ), tempfile.TemporaryDirectory() as (
            temp_dir_name
        ):
            vcftools_hap_r2_positions(
                temp_vcf=temp_vcf,
                temp_positions=temp_positions,
                chromosome=self.chromosome.char,
                interval=self.interval,
                output_path='{}/{}'.format(temp_dir_name, str(pos)),
                index_positions={pos},
                ld_threshold=0,
                population=None
            )
            with open(
                '{}/{}.list.hap.ld'.format(temp_dir_name, str(pos)), 'r',
            ) as f:
                f.readline()
                return tuple(
                    (
                        float(line.split()[5]),
                        position_to_variant_dict[int(line.split()[3])]
                    )
                    for line in f
                    if position_to_variant_dict.get(int(line.split()[3]))
                )
    
    def probability_mass_explained(self, trait, *annotations):
        self.credible_set(trait, probability_mass=1)
        annotations = set(annotations)
        return sum(
            variant.traits[trait].get('ppa', 0) for variant in self.variants
            if variant.annotations & annotations
        )
    
    def re_weight_lnbfs(self, trait, **annotations_logweights):
        annotations = set(annotations_logweights.keys())
        for variant in self.variants:
            if trait in variant.traits.keys():
                if (
                    (
                        variant.traits[trait].get('lnbf')
                        or variant.traits[trait].get('lnbf') == 0
                    )
                    and (variant.annotations & annotations)
                ):
                    for annotation in variant.annotations & annotations:
                        variant.traits[trait]['lnbf'] += annotations_logweights[
                            annotation
                        ]


class HeaderErrors():
    '''Errors for header parsing'''
    
    def raise_column_index_out_of_range(self, column_string, index, ncol):
        raise Exception(
            (
                'Error: The index provided to {}_arg was {}, but '
                'there are only {} columns in the variants file.'
            ).format(column_string, index + 1, ncol)
        )
    
    def raise_ambiguity(self, column_string):
        raise Exception(
             (
                'Error: No {} column was specified and the variants file '
                'header is ambiguous.'
            ).format(column_string)
        )
        
    def raise_bad_column_header(self, column_string):
        raise Exception(
            (
                'Error: The string provided to {}_arg is not in the variants '
                'file header.'
            ).format(column_string)
        )
        
    def raise_possible_delimiter_error(self):
        raise Exception(
            (
                'Error: There doesn\'t seem to be enough information in the '
                'variants file. Did you forget to set the delimiter with -d ?'
            )
        ) 


class VariantsHeader():
    """The header of an input variants file"""
    
    errors = HeaderErrors()
    
    def __init__(
        self,
        header,
        chromosome=None,
        position=None,
        id=None,
        locus=None,
        traits=None,
        trait=None,
        delimiter=None
    ):
        if isinstance(header, str):
            self.tuple = tuple(
                header.rstrip('\n').replace('\\t', '\t').split(
                    *((delimiter,) if delimiter else ())
                )
            )
        else:
            self.tuple = tuple(header)
        for column_string, arg in (
            (('chromosome', chromosome), ('position', position))
            + self.optional_variant_attribute('id', id)
            + self.optional_variant_attribute('locus', locus)
        ):
            self.get_index(column_string, arg)
        if traits:
            if isinstance(traits, dict):
                self.traits = traits
            else:
                self.traits = {}
                for trait, statistic, arg in traits:
                    try:
                        self.traits[trait][statistic] = int(arg)
                    except KeyError:
                        self.traits[trait] = {statistic: int(arg)}
                    except ValueError:
                        try:
                            self.traits[trait][statistic] = self.tuple.index(
                                arg
                            )
                        except ValueError:
                            self.traits[trait] = {
                                statistic: self.tuple.index(arg)
                            }
        elif trait:
            self.traits = {trait: {}}
            for index, colname in enumerate(self.tuple):
                if (
                    colname.casefold().startswith('p')
                    and ('val' in colname.casefold())
                ):
                    self.traits[trait]['pval'] = index
                elif (
                    colname.casefold().startswith('z')
                    and ('score' in colname.casefold())
                ):
                    self.traits[trait]['zscore'] = index
                elif colname.casefold() == 'beta':
                    self.traits[trait]['beta'] = index
                    for jndex, colname in enumerate(self.tuple):
                        if colname.casefold() in {'se', 'se_beta'}:
                            self.traits[trait]['se_beta'] = jndex
                elif colname.casefold() == 'maf':
                    self.traits[trait]['maf'] = index
                elif colname.casefold() == 'lnbf':
                    self.traits[trait]['lnbf'] = index
        else:
            self.traits = {}
          
    def __repr__(self):
        return repr(self.tuple)
    
    def __add__(self, variants_header):
        if set(self.traits.keys()) & set(variants_header.traits.keys()):
            raise Exception('Can\'t add two headers that share a trait')
        return VariantsHeader(
            (
                ('chr', 'pos', 'id')
                + self.non_basic_tuple()
                + variants_header.non_basic_tuple()
                + ('locus',) * (
                    hasattr(self, 'locus_index')
                    or hasattr(variants_header, 'locus_index')
                )
            ),
            traits=dict(
                itertools.chain(
                    (
                        (
                            trait,
                            {
                                stat: index + sum(
                                    index < item for item in {
                                        self.chromosome_index,
                                        self.position_index
                                    }
                                    | (
                                        {self.id_index}
                                        if hasattr(self, 'id_index')
                                        else {float('inf')}
                                    )
                                )
                                for stat, index in trait_contents.items()
                            }
                        )
                        for trait, trait_contents in self.traits.items()
                    ),
                    (
                        (
                            trait,
                            {
                                stat: index + len(self.tuple) - sum(
                                    index > item for item in {
                                        variants_header.chromosome_index,
                                        variants_header.position_index
                                    }
                                    | (
                                        {variants_header.id_index}
                                        if hasattr(variants_header, 'id_index')
                                        else {float('inf')}
                                    )
                                )
                                for stat, index in trait_contents.items()
                            }
                        )
                        for trait, trait_contents
                        in variants_header.traits.items()
                    )
                )
            )
        )
    
    def get_index(self, column_string, arg):
        try:
            self.check_argument_for_index(arg, column_string)
        except TypeError:
            for index, item in enumerate(self.tuple):
                if column_string == 'id':
                    column_name = item.casefold()
                    if check_id_condition(column_name):
                        self.first_ambiguity_check_and_index_assignment(
                            'id',
                            index
                        )
                elif column_string == 'position':
                    prefix = item.casefold()
                    if (
                        'position'.startswith(prefix)
                        or 'bposition'.startswith(prefix)
                    ):
                        self.first_ambiguity_check_and_index_assignment(
                            'position', index
                        )
                else:
                    prefix = item.casefold()
                    if column_string.startswith(prefix):
                        self.first_ambiguity_check_and_index_assignment(
                            column_string, index
                        )
            self.second_ambiguity_check(column_string)
        
    def check_argument_for_index(self, arg, column_string):
        try:
            index = int(arg)
            if index > len(self.tuple) or index < 0:
                self.errors.raise_column_index_out_of_range(
                    column_string, index, len(self.tuple)
                )
            else:
               setattr(self, '{}_index'.format(column_string), index)
        except ValueError:
            try:
                setattr(
                    self,
                    '{}_index'.format(column_string),
                    self.tuple.index(arg)
                )
            except ValueError:
                self.errors.raise_bad_column_header(column_string)
    
    def first_ambiguity_check_and_index_assignment(self, column_string, index):
        try:
            getattr(self, '{}_index'.format(column_string))
            self.errors.raise_ambiguity(column_string)
        except AttributeError:
            setattr(self, '{}_index'.format(column_string), index)
    
    def second_ambiguity_check(self, column_string):
        try:
            getattr(self, '{}_index'.format(column_string))
        except AttributeError:
            self.errors.raise_ambiguity(column_string)
    
    def optional_variant_attribute(self, column_string, arg):
        if column_string == 'id':
            if arg:
                return (('id', arg),)
            else:
                for index, item in enumerate(self.tuple):
                    column_name = item.casefold()
                    if check_id_condition(column_name):
                        return (('id', arg),)
                else:
                    return ()
        else:
            return (
                ((column_string, arg),) * bool(
                    arg
                    or
                    (column_string in (item.casefold() for item in self.tuple))
                )
            )
    
    def non_basic_tuple(self):
        return tuple(
            item for index, item in enumerate(self.tuple) if index not in {
                self.chromosome_index,
                self.position_index
            }
            | ({self.id_index} if hasattr(self, 'id_index') else set())
        )


class EQTLMappingHeader(VariantsHeader):
    
    def __init__(
        self,
        header,
        chromosome=None,
        position=None,
        id=None,
        gene=None,
        summary_statistics=None,
        delimiter=None
    ):
        super().__init__(
            header=header,
            chromosome=chromosome,
            position=position,
            id=id,
            delimiter=delimiter
        )
        self.get_gene_index(gene)
        self.get_summary_statistic_indices(summary_statistics)
    
    def get_gene_index(self, gene):
        try:
            self.check_argument_for_index(gene, 'gene')
        except TypeError:
            for index, item in enumerate(self.tuple):
                if item.casefold().startswith('gene'):
                    self.first_ambiguity_check_and_index_assignment(
                        'gene', index
                    )
            self.second_ambiguity_check('gene')
    
    def get_summary_statistic_indices(self, summary_statistics):
        if summary_statistics:
            self.summary_statistics = summary_statistics
        else:
            self.summary_statistics = {}
            for index, colname in enumerate(self.tuple):
                if (
                    colname.casefold().startswith('p')
                    and ('val' in colname.casefold())
                ):
                    self.summary_statistics['pval'] = index
                elif colname.casefold() in {'beta', 'slope'}:
                    self.summary_statistics['beta'] = index
                    for jndex, colname in enumerate(self.tuple):
                        if colname.casefold() in {
                            'se',
                            'se_beta',
                            'beta_se',
                            'se_slope',
                            'slope_se'
                        }:
                            self.summary_statistics['se_beta'] = jndex
                elif colname.casefold() == 'maf':
                    self.summary_statistics['maf'] = index
                elif colname.casefold() == 'lnbf':
                    self.summary_statistics['lnbf'] = index
        

class Variant():
    '''A variant'''
    
    raise_possible_delimiter_error = (
        HeaderErrors().raise_possible_delimiter_error
    )
    
    def __init__(self, tup, header):
        self.tuple = tup
        if len(self.tuple) < 2:
            self.raise_possible_delimiter_error()
        self.chromosome = casefold_chromosome_name(
            self.tuple[header.chromosome_index]
        )
        try:
            self.position = int(self.tuple[header.position_index])
        except ValueError:
            raise Exception(
                (
                    'Error: The position of a variant with the following tuple '
                    'representation could not be parsed as an integer:\n{}'
                ).format(repr(self.tuple))
            )
        self.id = (
            self.tuple[header.id_index].strip('"')
            if hasattr(header, 'id_index') else None
        )
        self.locus_name = (
            self.tuple[header.locus_index]
            if hasattr(header, 'locus_index') else None
        )
        self.annotations = set()
        self.traits = (
            {
                trait: {
                    statistic: try_float(tup[index])
                    for statistic, index in header.traits[trait].items()
                }
                for trait in header.traits.keys()
            }
            if hasattr(header, 'traits') else {}
        )
    
    def __repr__(self):
        return 'Variant({}, chr={}, pos={}, traits: {})'.format(
            self.id, self.chromosome, self.position, sorted(self.traits.keys())
        )
    
    def compute_zsq_from_pval(self, trait):
        try:
            self.traits[trait]['zsq'] = sumstats.zsq_from_pval(
                self.traits[trait]['pval']
            )
            return self.traits[trait]['zsq']
        except KeyError:
            raise Exception('This variant has no p-value for the given trait.')
    
    def compute_z_from_beta_se(self, *traits):
        for trait in traits:
            try:
                self.traits[trait]['zscore'] = (
                    self.traits[trait]['beta'] / self.traits[trait]['se_beta']
                )
            except KeyError:
                raise Exception(
                    'Variant {} has no beta or se for {}.'.format(self, trait)
                )
    
    def compute_lnbf(
        self,
        *traits,
        sample_size=None,
        cases=None,
        controls=None,
        prior_variance=None
    ):
        """preferentially uses beta/se approximation"""
        
        for trait in traits:
            if self.traits.get(trait):
                if self.traits[trait].get('lnbf') is None:
                    if (
                        (
                            (self.traits[trait].get('beta') is not None)
                            and self.traits[trait].get('se_beta')
                        )
                        or (
                            self.traits[trait].get('pval')
                            and self.traits[trait].get('maf')
                            and self.traits[trait].get('maf') != 1
                        )
                    ):
                        self.traits[trait]['lnbf'] = sumstats.approx_lnbf(
                            beta=self.traits[trait].get('beta'),
                            se_beta=self.traits[trait].get('se_beta'),
                            pval=self.traits[trait].get('pval'),
                            freq=self.traits[trait].get('maf'),
                            sample_size=sample_size,
                            cases=cases,
                            controls=controls,
                            prior_variance=prior_variance
                        )
            
    
    def format(self, header):
        format = {
            header.id_index: self.id,
            header.chromosome_index: self.chromosome,
            header.position_index: self.position
        }
        if hasattr(header, 'traits'):
            for trait in sorted(header.traits.keys()):
                for stat in sorted(header.traits[trait].keys()):
                    try:
                        format[header.traits[trait][stat]] = (
                            self.traits[trait][stat]
                        )
                    except KeyError:
                        format[header.traits[trait][stat]] = 'NA'
        self.tuple = tuple(val for key, val in sorted(format.items()))
    
    def get_normalized_tuple(self, header):
        return (
            (
                self.tuple[header.chromosome_index],
                self.tuple[header.position_index],
                (
                    self.tuple[header.id_index]
                    if hasattr(header, 'id_index') else 'NA'
                )
            )
            +
            tuple(
                item for index, item in enumerate(self.tuple) if index not in (
                    {
                        header.chromosome_index,
                        header.position_index
                     }
                    | (
                        {header.id_index}
                        if hasattr(header, 'id_index') else set()
                    )
                )
            )
        )


class IndexVariant(Variant):
    '''An index variant'''
    
    def __init__(self, tup, header):
        super().__init__(tup, header)
        if not hasattr(header, 'locus_index'):
            if ':' in self.id:
                self.id, self.locus_name = self.id.split(':')
            else:
                self.locus_name = self.id
    
    def __repr__(self):
        return 'IndexVariant({}, chr={}, pos={}, traits: {})'.format(
            self.id,
            self.chromosome,
            self.position,
            sorted(self.traits.keys())
        )




# Function Definitions ---------------------------------------------------------

def try_float(x):
    try:
        return float(x)
    except:
        return x


def casefold_chromosome_name(chromosome_name):
    return (
        str(chromosome_name)
        .casefold()
        .replace('chr', '')
        .replace('23', 'x')
        .replace('24', 'y')
        .replace('25', 'm')
        .upper()
    )


def construct_duplicate_lists(variants):
    duplicate_lists = {}
    prev_pos = 0
    prev_var = None
    for variant in variants:
        if variant.position == prev_pos:
            try:
                duplicate_lists[variant.position].append(variant)
            except KeyError:
                duplicate_lists[variant.position] = [prev_var, variant]
        prev_pos = variant.position
        prev_var = variant
    return duplicate_lists


def resolve_duplicates(
    duplicate_lists,
    variants,
    target_trait=None,
    stat=None,
    preserve_index_variants=True
):
    """Basically, each line from any GWAS file you load is read into a
    `funcgenom.Variant` object.

    If there are two or more duplicates with the same trait,
    `resolve_duplicate_variants` will merge the duplicates into one variant and
    keep the smallest lnbf, for the sake of being conservative. If there are two
    or more duplicates with different traits, it should merge them all into one
    variant with all the traits in a sensible way.
    """
    
    duplicate_variants = set()
    
    for position, duplicate_list in duplicate_lists.items():
        traits = {
            trait
            for variant in duplicate_list
            for trait in variant.traits.keys()
        }
        if not target_trait:
            target_trait = next(iter(traits))
        resolved_traits = {}
        for trait in traits:
            if check_stat_existence(duplicate_list, trait, 'maf'):
                conservative_maf = max(
                    variant.traits[trait].get('maf', float('-inf'))
                    for variant in duplicate_list
                    if (trait in variant.traits.keys())
                )
                try:
                    resolved_traits[trait]['maf'] = conservative_maf
                except KeyError:
                    resolved_traits[trait] = {'maf': conservative_maf}
            if check_stat_existence(duplicate_list, trait, 'lnbf'):
                conservative_lnbf = min(
                    variant.traits[trait].get('lnbf', float('inf'))
                    for variant in duplicate_list
                    if (trait in variant.traits.keys())
                )
                try:
                    resolved_traits[trait]['lnbf'] = conservative_lnbf
                except KeyError:
                    resolved_traits[trait] = {'lnbf': conservative_lnbf}
            if check_stat_existence(duplicate_list, trait, 'pval'):
                conservative_pval = max(
                    variant.traits[trait].get('pval', float('-inf'))
                    for variant in duplicate_list if (
                        trait in variant.traits.keys()
                    )
                )
                try:
                    resolved_traits[trait]['pval'] = conservative_pval
                except KeyError:
                    resolved_traits[trait] = {'pval': conservative_pval}
        stats = tuple(
            (
                float(
                    variant.traits[target_trait].get(
                        stat, float('inf') if stat == 'lnbf' else float('-inf')
                    )
                )
                if variant.traits.get(target_trait)
                else float('inf') if stat == 'lnbf' else float('-inf')
            )
            for variant in (
                (var for var in duplicate_list if isinstance(var, IndexVariant))
                if (
                    any(isinstance(var, IndexVariant) for var in duplicate_list)
                    and preserve_index_variants
                )
                else duplicate_list
            )
        )
        if stat in {'maf', 'pval'}:
            conservative_variant = duplicate_list[stats.index(max(stats))]
        elif stat == 'lnbf':
            conservative_variant = duplicate_list[stats.index(min(stats))]
        else:
            conservative_variant = duplicate_list[0]
        for trait in traits:
            if conservative_variant.traits.get(trait):
                for s in (
                    set(conservative_variant.traits[trait].keys())
                    - {'maf', 'lnbf', 'pval'}
                ):
                    try:
                        resolved_traits[trait][s] = (
                            conservative_variant.traits[trait][s]
                        )
                    except KeyError:
                        resolved_traits[trait] = {
                            s: conservative_variant.traits[trait][s]
                        }
        conservative_variant.traits = resolved_traits
        rsids = {
            variant.id
            for variant in duplicate_list
            if variant.id
            if RSID_REGEX.match(variant.id.split(',')[0])
            for rsid in variant.id.split(',')
        }
        if len(rsids) > 1:
            print(
                'Warning, mismatched rsids at {}:{} ({})'
                .format(
                    conservative_variant.chromosome,
                    conservative_variant.position,
                    ', '.join(rsids)
                )
            )
        conservative_variant.id = ','.join(rsids) if rsids else None
        duplicate_list.remove(conservative_variant)
        for variant in duplicate_list:
            duplicate_variants.add(variant)
            for trait in traits:
                if variant.traits.get(trait):
                    for s in (
                        set(variant.traits[trait].keys()) - {
                            'maf', 'lnbf', 'pval'
                        }
                    ):
                        try:
                            if not conservative_variant.traits[trait].get(s):
                                conservative_variant.traits[trait][s] = (
                                    variant.traits[trait][s]
                                )
                        except KeyError:
                            conservative_variant.traits[trait] = {
                                    s: variant.traits[trait][s]
                                }
    return [
        variant for variant in variants if variant not in duplicate_variants
    ]


def report_duplicate_removal(duplicate_lists, name):
    if (
        sum(
            len(duplicate_list)
            for position, duplicate_list in duplicate_lists.items()
        )
        > 0
    ):
        print(
            '{} duplicate variants were resolved at {}'.format(
                sum(
                    len(duplicate_list)
                    for position, duplicate_list in duplicate_lists.items()
                ),
                name
            )
        )


def resolve_and_report_duplicate_variants(
    variants,
    name,
    trait,
    stat,
    preserve_index_variants=True,
    report=False
):
    duplicate_lists = construct_duplicate_lists(variants)
    if report:
        report_duplicate_removal(duplicate_lists, name)
    return resolve_duplicates(
        duplicate_lists,
        variants,
        trait,
        stat,
        preserve_index_variants=preserve_index_variants
    )


def check_stat_existence(duplicate_list, trait, stat):
    return any(
        (stat in variant.traits[trait].keys()) for variant in duplicate_list
        if (trait in variant.traits.keys())
    )


def vcftools_hap_r2_positions(
    temp_vcf,
    temp_positions,
    chromosome,
    interval,
    output_path,
    index_positions,
    ld_threshold=0,
    population=None
):
    vcf = py1kgp.slice_vcf(
        chrom=chromosome,
        start=interval[0],
        end=interval[1],
        samples=population
    )
    temp_vcf.write(vcf)
    temp_positions.write(
        (
            '\n'.join(
                line for line in vcf.decode().split('\n') if  (
                    ((line[0] == '#') or (
                            int(line.split()[1]) in index_positions
                        )
                    )
                    if line != '' else True
                )
            )
        ).encode()
    )
    subprocess.call(
        (
            'vcftools',
            '--hap-r2-positions', temp_positions.name,
            '--vcf', temp_vcf.name,
            '--out', output_path,
            '--min-r2', str(ld_threshold)
        )
    )


def get_positions_in_ld(
    chromosome,
    interval,
    index_positions,
    ld_threshold=0.1,
    population=None
):
    with tempfile.NamedTemporaryFile() as (
        temp_vcf
    ), tempfile.NamedTemporaryFile() as (
        temp_positions
    ), tempfile.TemporaryDirectory() as (
        temp_dir_name
    ):
        vcftools_hap_r2_positions(
            temp_vcf=temp_vcf,
            temp_positions=temp_positions,
            chromosome=chromosome,
            interval=interval,
            output_path='{}/{}'.format(temp_dir_name, 'vcftools'),
            index_positions=index_positions,
            ld_threshold=ld_threshold,
            population=population
        )
        with open(
            '{}/{}.list.hap.ld'.format(temp_dir_name, 'vcftools'), 'r',
        ) as f:
            f.readline()
            positions_in_ld = { int(line.split()[3]) for line in f}
    return positions_in_ld


def annotate_variants(variant_positions, annotations, annotation_subset=None):
    annotations_per_variant = []
    for variant_position in variant_positions:
        annotations_per_variant.append(set())
        for annotation_name, interval_list in annotations.items():
            empty_interval_count = 0
            for interval in interval_list:
                if interval[1] < variant_position:
                    empty_interval_count += 1
                elif interval[0] > variant_position:
                    break
                else:
                    if annotation_subset:
                        if annotation_name in annotation_subset:
                            annotations_per_variant[-1].add(annotation_name)
                    else:
                        annotations_per_variant[-1].add(annotation_name)
                    break
            for x in range(empty_interval_count):
                interval_list.pop(0)
    return annotations_per_variant


def intersect_traits(obj, *traits):
    traits = set(traits)
    obj.variants = [
        variant for variant in obj.variants
        if traits <= set(variant.traits.keys())
    ]


def parse_variants_header(
    variants_file,
    add_header=None,
    replace_header=None,
    chromosome=None,
    position=None,
    id=None,
    locus=None,
    traits=None,
    trait=None,
    delimiter=None,
    vcf=False
):
    if add_header:
        header = VariantsHeader(
            header=add_header,
            chromosome=chromosome,
            position=position,
            id=id,
            locus=locus,
            traits=traits,
            trait=trait,
            delimiter=delimiter
        )
    elif replace_header:
        header = VariantsHeader(
            header=replace_header,
            chromosome=chromosome,
            position=position,
            id=id,
            locus=locus,
            traits=traits,
            trait=trait,
            delimiter=delimiter
        )
        variants_file.readline()
    else:
        header = VariantsHeader(
            header=(
                variants_file.readline() if not vcf else next(variants_file)[1:]
            ),
            chromosome=chromosome,
            position=position,
            id=id,
            locus=locus,
            traits=traits,
            trait=trait,
            delimiter=delimiter
        )
    return header


def parse_eqtl_mapping_header(
    eqtl_mapping_file,
    add_header=None,
    replace_header=None,
    chromosome=None,
    position=None,
    id=None,
    gene=None,
    summary_statistics=None,
    delimiter=None
):
    if add_header:
        header = EQTLMappingHeader(
            header=add_header,
            chromosome=chromosome,
            position=position,
            id=id,
            gene=gene,
            summary_statistics=summary_statistics,
            delimiter=delimiter
        )
    elif replace_header:
        header = EQTLMappingHeader(
            header=replace_header,
            chromosome=chromosome,
            position=position,
            id=id,
            gene=gene,
            summary_statistics=summary_statistics,
            delimiter=delimiter
        )
        eqtl_mapping_file.readline()
    else:
        header = EQTLMappingHeader(
            header=eqtl_mapping_file.readline(),
            chromosome=chromosome,
            position=position,
            id=id,
            gene=gene,
            summary_statistics=summary_statistics,
            delimiter=delimiter
        )
    return header


def compression_agnostic_open(file_path):
    return (
        gzip.open(file_path, 'rt')
        if file_path[-3:] == '.gz' else open(file_path, 'r')
    )


def chromosome_union(chrA, chrB, headerA, headerB, headerAB):
    if chrA.char != chrB.char:
        raise Exception('Cannot unify two chromosomes with different names')
    union = Chromosome(chrA.char)
    variants = concatenate_and_format_variants(
        chrA,
        chrB,
        headerA,
        headerB,
        headerAB
    )
    duplicate_pairs = construct_duplicate_lists(variants)
    duplicate_variants = {
        variant
        for duplicate_pair in duplicate_pairs.values()
        for variant in duplicate_pair
    }
    variants = [variant for variant in variants if variant not in duplicate_variants]
    for position, duplicate_pair in duplicate_pairs.items():
        if len(duplicate_pair) > 2:
            raise Exception('Resolve duplicates before unifying chromosomes')
        resolved_tuple = resolve_tuples(duplicate_pair, headerA)
        resolved_variant = Variant(resolved_tuple, headerAB)
        variants.append(resolved_variant)
    union.variants = sorted(variants, key=operator.attrgetter('position'))
    chrA.project_loci(union)
    chrB.project_loci(union)
    return union


def chromosome_intersection(chrA, chrB, headerA, headerB, headerAB):
    if chrA.char != chrB.char:
        raise Exception('Cannot intersect two chromosomes with different names')
    intersection = Chromosome(chrA.char)
    variants = concatenate_and_format_variants(
        chrA,
        chrB,
        headerA,
        headerB,
        headerAB
    )
    duplicate_pairs = construct_duplicate_lists(variants)
    for position, duplicate_pair in duplicate_pairs.items():
        if len(duplicate_pair) > 2:
            raise Exception(
                'Resolve duplicates before intersecting chromosomes'
            )
        resolved_tuple = resolve_tuples(duplicate_pair, headerA)
        resolved_variant = Variant(resolved_tuple, headerAB)
        intersection.variants.append(resolved_variant)
    intersection.sort_variants()
    chrA.project_loci(intersection)
    chrB.project_loci(intersection)
    return intersection


def concatenate_and_format_variants(chrA, chrB, headerA, headerB, headerAB):
    return sorted(
        itertools.chain(
            (
                (
                    IndexVariant(variant.get_normalized_tuple(headerA) + (('NA',) * (len(headerB.tuple) - 3)), headerAB)
                    if isinstance(variant, IndexVariant)
                    else Variant(variant.get_normalized_tuple(headerA) + (('NA',) * (len(headerB.tuple) - 3)), headerAB)
                )
                for variant in chrA.variants
            ),
            (
                (
                    IndexVariant(variant.get_normalized_tuple(headerB)[:3] + (('NA',) * (len(headerA.tuple) - 3)) + variant.get_normalized_tuple(headerB)[3:], headerAB)
                    if isinstance(variant, IndexVariant)
                    else Variant(variant.get_normalized_tuple(headerB)[:3] + (('NA',) * (len(headerA.tuple) - 3)) + variant.get_normalized_tuple(headerB)[3:], headerAB)
                )
                for variant in chrB.variants
            )
        ),
        key=operator.attrgetter('position')
    )


def resolve_tuples(duplicate_pair, headerA):
    return (
        duplicate_pair[0].tuple[:len(headerA.tuple)]
        + duplicate_pair[1].tuple[len(headerA.tuple):]
    )


def check_id_condition(column_name):
    return (
        column_name in {'id', 'marker', 'markername', 'snp'} or (
            column_name.startswith(('rs', 'snp', 'variant', 'marker'))
            and column_name.endswith('id')
        )
    )


def genome_or(genome0, genome1):
    return genome0 | genome1


def genome_and(genome0, genome1):
    return genome0 & genome1


def union_of_oversized_genomes(genome0, genome1, processes=1):
    union = Genome()
    union.variants_header = (genome0.variants_header + genome1.variants_header)
    for chromosome_name in tuple(range(1,23)) + ('X', 'Y', 'M'):
        if (
            genome0.chromosome.get(chromosome_name)
            and (not genome1.chromosome.get(chromosome_name))
        ):
            union.add_chromosome(genome0.chromosome[chromosome_name])
        elif (
            (not genome0.chromosome.get(chromosome_name))
            and genome1.chromosome.get(chromosome_name)
        ):
            union.add_chromosome(genome1.chromosome[chromosome_name])
    if processes == 1:
        for single_chromosome in (
            (
                genome0.extract_chromosomes(name)
                | genome1.extract_chromosomes(name)
            )
            for name in common_chromosome_names(genome0, genome1)
        ):
            union = union + single_chromosome
    else:
        with Pool(processes=processes) as pool:
            for single_chromosome in pool.starmap(
                genome_or,
                common_chromosomes_extracted_and_paired(genome0, genome1)
            ):
                union = union + single_chromosome
    return union


def intersection_of_oversized_genomes(genome0, genome1, processes=1):
    intersection = Genome()
    intersection.variants_header = (
        genome0.variants_header
        + genome1.variants_header
    )
    if processes == 1:
        for single_chromosome in (
            (
                genome0.extract_chromosomes(name)
                & genome1.extract_chromosomes(name)
            )
            for name in common_chromosome_names(genome0, genome1)
        ):
            intersection = intersection + single_chromosome
    else:
        with Pool(processes=processes) as pool:
            for single_chromosome in pool.starmap(
                genome_and,
                common_chromosomes_extracted_and_paired(genome0, genome1)
            ):
                intersection = intersection + single_chromosome
    return intersection


def common_chromosome_names(genome0, genome1):
    return (
        name for name in tuple(range(1, 23)) + ('X', 'Y', 'M') if name in (
            set(genome0.chromosome.keys())
            & set(genome1.chromosome.keys())
        )
    )


def common_chromosomes_extracted_and_paired(genome0, genome1):
    return (
        (genome0.extract_chromosomes(name), genome1.extract_chromosomes(name))
        for name in common_chromosome_names(genome0, genome1)
    )


def separate_genes_and_variants(genes_and_variants):
    genes = {
        arg for arg in genes_and_variants
        if isinstance(arg, str)
        if not RSID_REGEX.match(arg)
    }
    variant_coordinates = {
        (
            (variant.chromosome, variant.position)
            if isinstance(variant, Variant) else (
                pyhg19.coord_tuple(variant)
                if isinstance(variant, str) else variant
            )
        )
        for variant in set(genes_and_variants) - genes
    }
    return genes, variant_coordinates


def eqtl_benjamini_hochberg(variant_gene_pairs, false_discovery_rate):
    number_of_hypotheses = len(variant_gene_pairs)
    sorted_pval_variant_gene_trios = sorted(
        (variant.traits[gene]['pval'], variant, gene)
        for variant, gene in variant_gene_pairs
    )
    for index, pval_variant_gene_trio in enumerate(
        sorted_pval_variant_gene_trios
    ):
        pval, variant, gene = pval_variant_gene_trio
        if pval <= (index + 1) / number_of_hypotheses * false_discovery_rate:
            significant_results = sorted_pval_variant_gene_trios[:index + 1]
    return (
        (variant, gene) for pval, variant, gene in significant_results
    ) 


def look_up_rsid(variant, graceful=False):
    if graceful:
        try:
            return pyhg19.rsid(variant.chromosome, variant.position)
        except:
            return None
    else:
        return pyhg19.rsid(variant.chromosome, variant.position)




# Errors =======================================================================

class Error(Exception):
   '''Base class for other exceptions'''
   pass


class BadArgumentError(Error):
    '''Bad argument error'''
    pass
