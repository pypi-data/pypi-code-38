from os.path import join


def create_xml_description(path, file="251.xml", verbose=False):
    """Create a peculiar xml file used by Protein Global Server for no known reason.

    Developpers of PLGS are asked to provide explanations on all their misdeeds.

    Arguments
    =========
    path : str
        Path to the folder where the xml file should be dumped.
    file : str
        Name of the file.
    """
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <WORKFLOW_TEMPLATE TITLE="default search" UUID="f499a2d3-22f0-4ab6-b0d9-0999d01e543f" WORKFLOW_TEMPLATE_ID="_13927376466640_5646062711616823">
        <PROTEINLYNX_QUERY TYPE="Databank-search">
            <DATABANK_SEARCH_QUERY_PARAMETERS>
                <SEARCH_ENGINE_TYPE VALUE="PLGS"/>
                <SEARCH_DATABASE NAME="UNIPROT"/>
                <SEARCH_TYPE NAME="Electrospray-Shotgun"/>
                <IA_PARAMS>
                    <FASTA_FORMAT VALUE="DEF"/>
                    <PRECURSOR_MHP_WINDOW_PPM VALUE="-1"/>
                    <PRODUCT_MHP_WINDOW_PPM VALUE="-1"/>
                    <NUM_BY_MATCH_FOR_PEPTIDE_MINIMUM VALUE="2"/>
                    <NUM_PEPTIDE_FOR_PROTEIN_MINIMUM VALUE="1"/>
                    <NUM_BY_MATCH_FOR_PROTEIN_MINIMUM VALUE="5"/>
                    <PROTEIN_MASS_MAXIMUM_AMU VALUE="2500000"/>
                    <FALSE_POSITIVE_RATE VALUE="1"/>
                    <AQ_PROTEIN_ACCESSION VALUE=""/>
                    <AQ_PROTEIN_MOLES VALUE="-1"/>
                    <MANUAL_RESPONSE_FACTOR VALUE="1000"/>
                    <DIGESTS>
                        <ANALYSIS_DIGESTOR MISSED_CLEAVAGES="2">
                            <AMINO_ACID_SEQUENCE_DIGESTOR NAME="Trypsin" UUID="50466de0-ff04-4be2-a02f-6ccc7b5fd1f5">
                                <CLEAVES_AT AMINO_ACID="K" POSITION="C-TERM">
                                    <EXCLUDES AMINO_ACID="P" POSITION="N-TERM"/>
                                </CLEAVES_AT>
                                <CLEAVES_AT AMINO_ACID="R" POSITION="C-TERM">
                                    <EXCLUDES AMINO_ACID="P" POSITION="N-TERM"/>
                                </CLEAVES_AT>
                            </AMINO_ACID_SEQUENCE_DIGESTOR>
                        </ANALYSIS_DIGESTOR>
                    </DIGESTS>
                    <MODIFICATIONS>
                        <ANALYSIS_MODIFIER STATUS="FIXED">
                            <MODIFIER MCAT_REAGENT="No" NAME="Carbamidomethyl+C">
                                <MODIFIES APPLIES_TO="C" DELTA_MASS="57.0215" TYPE="SIDECHAIN"/>
                            </MODIFIER>
                        </ANALYSIS_MODIFIER>
                        <ANALYSIS_MODIFIER ENRICHED="FALSE" STATUS="VARIABLE">
                            <MODIFIER MCAT_REAGENT="No" NAME="Oxidation+M">
                                <MODIFIES APPLIES_TO="M" DELTA_MASS="15.9949" TYPE="SIDECHAIN"/>
                            </MODIFIER>
                        </ANALYSIS_MODIFIER>
                    </MODIFICATIONS>
                </IA_PARAMS>
            </DATABANK_SEARCH_QUERY_PARAMETERS>
        </PROTEINLYNX_QUERY>
    </WORKFLOW_TEMPLATE>"""
    with open(join(path, file), "w") as h:
        h.write(xml)
    if verbose:
        print("Created the {} file.".format(file))