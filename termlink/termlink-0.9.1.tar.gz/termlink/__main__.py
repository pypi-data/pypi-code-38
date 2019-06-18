"""The main program.

This module is the command line interface for running "termlink."
"""
import argparse
import textwrap

from termlink import common
from termlink import gsea
from termlink import codesystem

from termlink.configuration import Config

from termlink.rxnorm import Command as RxNormCommand
from termlink.hpo import Command as HPOCommand
from termlink.snomedct import Command as SnomedCtCommand

configuration = Config()
logger = configuration.logger

parser = argparse.ArgumentParser(
    description="""
    An ontology conversion toolkit for the Precision Health Cloud.
    """
)

subparsers = parser.add_subparsers(
    title="Commands",
    metavar=""
)

parser_common = subparsers.add_parser(
    "common",
    help="Convert a common format ontology",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""
    Convert an ontology represented in a common format.

    Supported format types:
      - OBO (obo)
      - RDF/XML (owl)
    """)
)

parser_common.add_argument(
    "uri",
    metavar="URI",
    help="resource identifier for files"
)

parser_common.add_argument(
    "-s",
    "--system",
    help="identity of the terminology system",
    required=True
)

parser_common.set_defaults(execute=common.execute)

parser_hpo = subparsers.add_parser(
    "hpo",
    help="Convert the 'Human Phenotype Ontology'",
    description="""
    The Human Phenotype Ontology (HPO) project provides an ontology of medically relevant phenotypes, disease-phenotype annotations, and the algorithms that operate on these. The HPO can be used to support differential diagnostics, translational research, and a number of applications in computational biology by providing the means to compute over the clinical phenotype. The HPO is being used for computational deep phenotyping and precision medicine as well as integration of clinical data into translational research. Deep phenotyping can be defined as the precise and comprehensive analysis of phenotypic abnormalities in which the individual components of the phenotype are observed and described. The HPO is being increasingly adopted as a standard for phenotypic abnormalities by diverse groups such as international rare disease organizations, registries, clinical labs, biomedical resources, and clinical software tools and will thereby contribute toward nascent efforts at global data exchange for identifying disease etiologies (Köhler et al, 2017). [1]
    """,
    epilog="""
    [1] Human Phenotype Ontology. Retrieved April 29, 2019, from https://hpo.jax.org/app/help/introduction
    """
)

parser_hpo.add_argument(
    "uri",
    metavar="URI",
    help="resource identifier for files"
)

parser_hpo.add_argument(
    "--skip-alt-ids",
    dest='skip_alt_ids',
    action='store_true',
    help="skips 'alt_id' references"
)

parser_hpo.add_argument(
    "--skip-synonyms",
    dest='skip_synonyms',
    action='store_true',
    help="skips 'synonym' references"
)

parser_hpo.set_defaults(execute=HPOCommand.execute)
parser_hpo.set_defaults(skip_alt_ids=False)
parser_hpo.set_defaults(skip_synonyms=False)


parser_rxnorm = subparsers.add_parser(
    "rxnorm",
    help="Convert the 'RxNorm' code system",
    description="""
    RxNorm provides normalized names for clinical drugs and links its names to
    many of the drug vocabularies commonly used in pharmacy management and drug
    interaction software, including those of First Databank, Micromedex, 
    Gold Standard Drug Database, and Multum. By providing links between these 
    vocabularies, RxNorm can mediate messages between systems not using the 
    same software and vocabulary. [1] 

    Additional source vocabularies, aside from RxNorm, must be specified using 
    the --vocabulary option. The full list of available source vocabularies is 
    available at https://www.nlm.nih.gov/research/umls/rxnorm/docs/2019/rxnorm_doco_full_2019-1.html#s3_0.

    By default concepts that are not suppressed, specified by the 'N' flag, are
    included in the output. Additional flags can be included using the --suppress
    option. More information on suppression can is documented at https://www.nlm.nih.gov/research/umls/rxnorm/docs/2019/rxnorm_doco_full_2019-1.html#s12_0.
    """,
    epilog="""
    [1] RxNorm. Retrieved April 22, 2019, from https://www.nlm.nih.gov/research/umls/rxnorm/
    """
)

parser_rxnorm.add_argument(
    "uri",
    metavar="URI",
    help="resource identifier for files"
)

parser_rxnorm.add_argument(
    "-v",
    "--vocabulary",
    action='append',
    default=['RXNORM'],
    help="use an additional source vocabulary (default: 'RXNORM')"
)

parser_rxnorm.add_argument(
    "-s",
    "--suppress",
    action='append',
    default=['N'],
    help="unset the provided suppress flag (default: 'N')"
)

parser_rxnorm.set_defaults(execute=RxNormCommand.execute)

parser_gsea = subparsers.add_parser(
    "gsea",
    help="Convert the 'Gene Set Enrichment Analysis Ontology'",
    description="""
    The Gene Set Enrichment Analysis Ontology (GSEA) project provides an ontology of genes grouped by a 
    relational concept. [1]
    """,
    epilog="""
    [1] Gene Set Enrichment Analysis Ontology. Retrieved May 8, 2019, from http://software.broadinstitute.org/gsea/msigdb/collections.jsp
    """
)

parser_gsea.add_argument(
    "uri",
    metavar="URI",
    help="resource identifier for files"
)

parser_gsea.set_defaults(execute=gsea.execute)

parser_snomedct = subparsers.add_parser(
    "snomed-ct",
    help="Convert the 'SNOMED-CT' code system",
    description="""
    SNOMED CT is a clinical terminology with global scope covering a wide range of clinical specialties, disciplines and requirements. As a result of its broad scope, one of the benefits of SNOMED CT is a reduction of specialty boundary effects that arise from use of different terminologies or coding systems by different clinicians or departments. 
    This allows wider sharing and reuse of structured clinical information. Another benefit of SNOMED CT is that the same data can be processed and presented in ways that serve different purposes. For example, clinical records 
    represented using SNOMED CT can be processed and presented in different ways to support direct patient care, clinical audit, research, epidemiology, management and service planning. Additionally, the global scope of SNOMED CT reduces geographical boundary effects arising from the use of different terminologies or coding systems in different organizations and countries. [1]
    """,
    epilog="""
    [1] Snomed-CT. Retrieved May 9, 2019 from https://confluence.ihtsdotools.org/display/DOCSTART/3.+Using+SNOMED+CT+in+Clinical+Information
    """
)

parser_snomedct.add_argument(
    "uri",
    metavar="URI",
    help="resource identifier for files"
)

parser_snomedct.add_argument(
    "--versioned",
    dest='versioned',
    action='store_true',
    help="includes 'version' mapping"
)

parser_snomedct.add_argument(
    "--include-inactive",
    dest='include_inactive',
    action='store_true',
    help="includes 'inactive' relationship"
)

parser_snomedct.set_defaults(execute=SnomedCtCommand.execute)

parser_codesystem = subparsers.add_parser(
    "code-system",
    help="Convert a FHIR CodeSystem Resource",
    description="""
    The CodeSystem resource is used to declare the existence of and describe a code system or code system supplement and its key properties, and optionally define a part or all of its content.
    """,
    epilog="""
    [1] “4.8 Resource CodeSystem - Content.” CodeSystem - FHIR v4.0.0, Retrieved June 5, 2019 from www.hl7.org/fhir/codesystem.html.
    """
)

parser_codesystem.add_argument(
    "uri",
    metavar="URI",
    help="resource identifier for files"
)

parser_codesystem.set_defaults(execute=codesystem.execute)


args = parser.parse_args()

if hasattr(args, 'execute'):
    args.execute(args)
else:
    parser.print_help()

