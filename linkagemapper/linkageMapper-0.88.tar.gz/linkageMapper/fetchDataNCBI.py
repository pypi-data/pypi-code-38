#!/bin/python

"""

Downloads assemblies found on 'assembly' entrez database,
 they are fetched from 'nucleotide' database.

"""

from Bio import Entrez, SeqIO
import gzip
import json
import os
import re

import random

import shutil

import ftplib
import optparse
import time

from linkageMapper.Database import StrainNames
import socket
# is this legal in the terms of the LAW?
Entrez.email = 'researcher_%i@one-time-use.cn' % random.randrange(0, 1000)


class FTPConnection():
    def __init__(self, ftpServerAddress):
        self.ftpServerAddress = ftpServerAddress

        self.cdir = None

        # ftp connection settings;
        self.timeout = 180
        self.retries = 5
        self.launch()

    def launch(self):
        self.f = ftplib.FTP(self.ftpServerAddress, timeout=self.timeout)
        self.f.login()

        if self.cdir:
            self.cd(self.cdir)

    def cd(self, ftpDirectory):
        self.cdir = ftpDirectory
        self.execute(self.f.cwd, ftpDirectory)

    def listdir(self):
        return self.execute(self.f.nlst)

    def downloadFile(self,
                     remoteFileName,
                     localfilepath):

        with open(localfilepath, 'wb') as localFile:

            downloaded = self.f.retrbinary(
                "RETR %s" % (remoteFileName),
                localFile.write,
                blocksize=32 * 1024)

        return downloaded

    def execute(self, operation, *args):
        for k in range(self.retries):
            if k == self.retries - 1:
                print("Failure... re-running this script should solve.")
                exit(1)
            try:
                result = operation(*args)
                return result

            except (EOFError, TimeoutError,
                    socket.timeout, ftplib.error_temp) as e:
                print("Failure to execute %s on try #%i retries." %
                      (operation.__name__,
                       k + 1))
                print(e)
                try:
                    self.f.quit()
                except Exception:
                    time.sleep(5)
                    self.execute(self.launch)
                    time.sleep(3)
                    print("Retrying....")

            except BrokenPipeError as e:
                raise e

        return result


class DownloadQuery():
    def __init__(self, IDs, downloadDirectory, FileTypes):
        self.IDs = IDs
        self.downloadDirectory = downloadDirectory
        self.FileTypes = FileTypes

    def execute(self):
        DownloadSuccess = False

        for d, ID in enumerate(self.IDs):
            print("Downloading %i of %i.\n" % (d + 1, len(self.IDs)))

            FileSuccess = downloadAssembly(ID,
                                           downloadDirectory=self.downloadDirectory,
                                           onlyCompleteGenome=True,
                                           wantedFileTypes=self.FileTypes)
            if FileSuccess:
                DownloadSuccess = True

        return DownloadSuccess


def debug(message):
    print('Debug ---> %s' % message)


def findAssemblyList(Organism, Strain=None, retmax=100):
    query = '("%s"[Organism] AND "latest"[Filter]' % Organism
    if Strain:
        query += ' AND "%s"[Strain]' % Strain
    result = Entrez.esearch(db='assembly', term=query, retmax=retmax)

    P = Entrez.read(result)

    print(json.dumps(P, indent=2))
    return P['IdList']


def downloadAssembly(ID,
                     downloadDirectory='',
                     showSummaries=False,
                     onlyCompleteGenome=True,
                     wantedFileTypes=[],
                     Verbose=False):
    print(ID)
    Summary = Entrez.esummary(db="assembly", id=ID, report='full')
    Summary = Entrez.read(Summary, validate=False)
    relevantSummary = Summary['DocumentSummarySet']['DocumentSummary'][0]

    # return Summary
    nucl_id = relevantSummary['AssemblyAccession']

    # print(json.dumps(relevantSummary, indent=2))

    if showSummaries:
        debug("Assembly Summary %s" % json.dumps(Summary, indent=4))
    assemblyStatus = relevantSummary['AssemblyStatus']
    genomeRepresentation = relevantSummary["PartialGenomeRepresentation"]

    debug(assemblyStatus)

    entrySpecies = relevantSummary["Organism"]

    strainData = relevantSummary["Biosource"]["InfraspeciesList"]

    entryStrain = strainData[0]["Sub_value"] if strainData else ''
    print("%s %s" % (entrySpecies, entryStrain))

    print()
    print()

    if onlyCompleteGenome:
        print("Genome Representation is %s" % genomeRepresentation)
        if genomeRepresentation not in ["full", "false"]:
            debug("Skipping partial genome.")
            return 0
        """
        if assemblyStatus != 'Complete Genome':
            debug("Skipping scaffold entry.")
            return 0
        """

    ftpPath = relevantSummary['FtpPath_GenBank']

    debug(ftpPath)

    ftpDirectory = re.findall("genome.*", ftpPath)
    if not ftpDirectory:
        debug("No ftp directory associated. Skipping...")
        return False
    else:
        ftpDirectory = ftpDirectory[0]

    ftpServerAddress = re.findall("ftp\..*gov", ftpPath)[0]
    debug(ftpServerAddress)

    # -- instantiate FTP connection;
    Connection = FTPConnection(ftpServerAddress)
    Connection.cd(ftpDirectory)

    # FETCH FTP DIRECTORY FILE LIST;
    remoteFiles = Connection.listdir()

    if not wantedFileTypes:
        wantedFileTypes = [
            '_feature_table',
            '_genomic.gff',
            '_genomic.gbff',
            '_genomic.fna'
        ]

    remoteFileExtension = None
    remoteFileNames = []
    for File in remoteFiles:
        for wantedFileType in wantedFileTypes:
            if wantedFileType in File:
                remoteFileNames.append(File)
                remoteFileExtension = "." + wantedFileType.split(".")[-1]

    # download only the file with shortest name among matched files at FTP directory;
    remoteFileNames = sorted(remoteFileNames,
                             key=lambda x: len(x))[0: 1]

    showRemoteFiles = True
    if not remoteFileNames or showRemoteFiles:
        if remoteFileNames:
            print("Found %s." % ' '.join(remoteFileNames))
        else:
            print("Remote file key %s not found on FTP server." %
                  ' '.join(wantedFileTypes))
            return 0

        print("\nRemote files: " + "=" * 10)
        print('\n'.join(remoteFiles))
        print()
        print("=" * 22)
        print()

    DownloadSuccess = False
    for remoteFileName in remoteFileNames:
        localFileName = remoteFileName

        localfilepath = os.path.join(downloadDirectory, localFileName)
        debug("Writing assembly to %s" % localfilepath)

        debug("Downloading %s" % remoteFileName)

        downloaded = Connection.execute(
            Connection.downloadFile, remoteFileName, localfilepath)

        debug(remoteFileName)
        debug("download result: %s" % downloaded)

        DownloadSuccess = True

        # GUNZIP FILE - decompress;
        if localfilepath.endswith(".gz"):
            with gzip.open(localfilepath, 'rb') as gf:
                file_content = gf.read()
                decompressedPath = os.path.splitext(localfilepath)[0]
                open(decompressedPath, 'wb').write(file_content)
                debug("Decompressed to %s." % decompressedPath)
                os.remove(localfilepath)
                localfilepath = decompressedPath
                print('\n')

    return DownloadSuccess


def strainToDatabase(species):
    P = findAssemblyList(species)
    debug("number of entries: %i" % len(P))
    GenomeCount = 0
    ChromosomeCount = 0

    for Entry in P:
        print("*" * 17)
        n = downloadAssembly(Entry, downloadDirectory='../Analysis/')
        if n:
            GenomeCount += 1
            ChromosomeCount += n

    print("Found %i chromosomes on %i genomes for %s" % (
        ChromosomeCount,
        GenomeCount,
        species))


def renameGenomeFiles(dirpath, organism):
    allGenomes = os.listdir(dirpath)
    allGenomes = [g for g in allGenomes if g.endswith(".fna", ".fasta")]
    def orderByVersion(g):
        for version in range(10, 1, -1):
            if "v%i_" in g.lower():
                return version
        return 1

    allGenomes = sorted(allGenomes, key=orderByVersion)
    for genome in allGenomes:
        localfilepath = os.path.join(dirpath, genome)
        genome = list(SeqIO.parse(localfilepath, format='fasta'))

        if not genome:
            print("Error parsing genome!")
            print("Filename: %s" % localfilepath)
            print(genome)
            continue

        genomeDescription = genome[0].description
        strainName = StrainNames.fetchStrainName(genomeDescription, organism)

        if strainName is not None:
            newFilePath = os.path.join(os.path.dirname(localfilepath),
                                       strainName + '.fna')
            shutil.move(localfilepath, newFilePath)
            print("Moving genome %s file to %s" % (localfilepath, newFilePath))


def parse_options():
    parser = optparse.OptionParser()
    parser.add_option("--nogenome",
                      dest='downloadGenomes',
                      action='store_false',
                      default=True,
                      help="Skip genome downloads.")

    parser.add_option("--noannotation",
                      dest='downloadAnnotations',
                      action='store_false',
                      default=True,
                      help="Skip annotation downloads.")

    parser.add_option("--organism",
                      dest="queryOrganism",
                      default="Toxoplasma gondii")

    parser.add_option("--strain",
                      dest="annotationStrain",
                      default="")

    parser.add_option("--maxgenomecount",
                      dest="genomeSearchMaxResults",
                      type=int,
                      default=20)

    options, args = parser.parse_args()

    return options


def main():
    options = parse_options()

    # -- Make sure output directories exist;
    requiredDirectories = ["genomes", "annotations"]
    for Dir in requiredDirectories:
        if not os.path.isdir(Dir):
            os.mkdir(Dir)

    # -- Search Assemblies for Organism;
    AssemblyIDs = findAssemblyList(options.queryOrganism,
                                   retmax=options.genomeSearchMaxResults)

    # -- DOWNLOAD GENOMES;
    dataTypes = []
    # Fetch Genome IDs;
    if options.downloadGenomes:
        dataTypes.append(DownloadQuery(AssemblyIDs,
                                       "genomes",
                                       ["_genomic.fna"]))

    # Download genomes
    GenomeDownloadSuccess = [query.execute() for query in dataTypes]

    AnnotationDownloadSuccess = []
    # -- DOWNLOAD ANNOTATIONS;
    print("\nFetching Annotations.\n")
    dataTypes = []
    # Fetch Annotation IDs;
    if options.downloadAnnotations:
        # DEPRECATED;
        if not options.annotationStrain:
            # Try to find an annotation that matches any genome,
            annotationStrains = [f.replace("_", " ").split(".")[0]
                                 for f in os.listdir("genomes")]
        if options.annotationStrain:
            # Try to find the user-defined annotation;
            # Fetch user-defined annotation;
            AnnotationIDs = findAssemblyList(options.queryOrganism,
                                             Strain=options.annotationStrain,
                                             retmax=options.genomeSearchMaxResults)

            if AnnotationIDs:
                print("Found Annotation IDs:")
                for i in AnnotationIDs:
                    print(i)
                print()

                dataTypes.append(DownloadQuery(AnnotationIDs,
                                               "annotations",
                                               ["_genomic.gbff"]))
                dataTypes.append(DownloadQuery(AnnotationIDs,
                                               "genomes",
                                               ["_genomic.fna"]))
            else:
                print("User defined annotation strain %s not found!" %
                      options.annotationStrain)
                print("Aborting...")
                exit(1)

        else:
            # Try to download a genome that has a matching annotation;
            print("Annotation not found.")
            dataTypes.append(DownloadQuery(AssemblyIDs, "annotations", ["_genomic.gbff"]))

        AnnotationDownloadSuccess = [query.execute() for query in dataTypes]

    # -- REPORT SUCCESS (any?);
    print("\nSummary:")
    if any(GenomeDownloadSuccess):
        print("Genome files downloaded.")

        # properly name genome files;
        renameGenomeFiles("genomes", options.queryOrganism)

    if any(AnnotationDownloadSuccess):
        print("Annotation files downloaded.")


if __name__ == "__main__":
    main()
