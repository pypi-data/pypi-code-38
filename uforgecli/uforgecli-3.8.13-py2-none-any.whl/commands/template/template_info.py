__author__ = "UShareSoft"

from hurry.filesize import size
from uforgecli.utils.extract_id_utils import extractId
from uforgecli.utils.string_utils import strftime_if_not_none, convert_boolean_to_yes_or_no, xstr
from uforgecli.utils.texttable_utils import init_texttable
from ussclicore.utils import generics_utils
from ussclicore.utils import printer

class TemplateInfo:
    def __init__(self, api, user_account, appliance, print_details):
        self.api = api
        self.user_account = user_account
        self.appliance = appliance
        self.print_details = print_details

    def print_main_info(self):
        printer.out("Main information about " + str(self.appliance.name), printer.INFO)
        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])

        table.add_row(["Name", self.appliance.name])
        table.add_row(["Id", self.appliance.dbId])
        table.add_row(["Version", self.appliance.version])
        table.add_row(["Uri", self.appliance.uri])
        table.add_row(["Created", strftime_if_not_none(self.appliance.created)])
        table.add_row(["Last Modified", strftime_if_not_none(self.appliance.lastModified)])
        table.add_row(["Last Package Update", strftime_if_not_none(self.appliance.lastPkgUpdate)])
        table.add_row(["Available OS Updates", self.get_nb_updates()])

        shared = convert_boolean_to_yes_or_no(self.appliance.shared)
        table.add_row(["Shared", shared])

        imported = convert_boolean_to_yes_or_no(self.appliance.imported)
        table.add_row(["Cloned from App Store", imported])

        table.add_row(["Description", self.appliance.description])

        print table.draw() + "\n"

    def get_nb_updates(self):
        if self.appliance.nbUpdates < 0:
            return 0
        else:
            return self.appliance.nbUpdates

    def print_install_settings(self):
        install_profile = self.appliance.installProfile
        if install_profile is None:
            printer.out("No Install Settings", printer.INFO)
            return

        printer.out("Install Settings", printer.INFO)
        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])

        if install_profile.rootUser is not None and install_profile.rootUser.passwordAuto:
            table.add_row(["Password", install_profile.rootUser.password])
        else:
            table.add_row(["Password", "Asked during first boot or install"])

        if install_profile.internetSettingsAuto:
            table.add_row(["Internet Settings", "DHCP"])
        else:
            table.add_row(["Internet Settings", "Asked during first boot or install"])

        if install_profile.seLinuxMode:
            table.add_row(["SELinux mode", install_profile.seLinuxMode])

        if install_profile.skipLicenses:
            table.add_row(["Licensing", "skipped"])
        else:
            table.add_row(["Licensing", "shown at first boot or install"])

        if install_profile.timezoneAuto:
            table.add_row(["Time Zone", install_profile.timezone])
        else:
            table.add_row(["Time Zone", "asked during first boot or install"])

        self.__prepare_disks_and_partitions(table, install_profile)

        print table.draw() + "\n"

    def __prepare_disks_and_partitions(self, table, install_profile):
        if install_profile.partitionTable is None:
            printer.out("No partition table", printer.INFO)
            return

        for index, disk in enumerate(install_profile.partitionTable.disks.disk, start=1):
            table.add_row(["Disk " + str(index), disk.name + " " + str(disk.size) + " MB " + disk.partitionType])
            self.__prepare_partitions(table, disk)

    def __prepare_partitions(self, table, disk):
        for index, partition in enumerate(disk.partitions.partition, start=1):
            self.__prepare_partition(table, disk, partition, index)
            self.__prepare_logical_partitions(table, partition.logicalPartitions.logicalPartition)

    def __prepare_partition(self, table, disk, partition, partition_number):
        table.add_row(["Partition " + str(partition_number),
                       disk.name + partition.name + " " + str(partition.size) + " MB " + xstr(
                           partition.fstype) + " " + xstr(partition.mpoint) + " " + xstr(partition.label) + " " + xstr(
                           self.get_partition_growable(partition))])

    def __prepare_logical_partitions(self, table, logical_partitions):
        for index, logical_partition in enumerate(logical_partitions, start=1):
            self.__prepare_logical_partition(table, logical_partition, index)

    def __prepare_logical_partition(self, table, logical_partition, logical_partition_number):
        table.add_row(["Logical Partition " + str(logical_partition_number),
                       logical_partition.name + " " + str(logical_partition.size) + " MB " + xstr(
                           logical_partition.fstype) + " " + xstr(
                           logical_partition.mpoint) + " " + xstr(logical_partition.label) + " " + xstr(self.get_partition_growable(logical_partition))])

    def get_partition_growable(self, partition):
        if partition.growable:
            return "grow"
        else:
            return None

    def print_os_profile(self):
        printer.out("OS Profile", printer.INFO)
        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])

        table.add_row(["OS", str(self.appliance.distributionName) + " " + str(self.appliance.archName)])

        if self.appliance.osProfile is not None:
            table.add_row(["OS Profile Name", self.appliance.osProfile.name])

            if hasattr(self.appliance.osProfile, "packagesUri") and self.appliance.osProfile.packagesUri is not None:
                self.__prepare_linux_os_profile(table)

        print table.draw() + "\n"

    def __prepare_linux_os_profile(self, table):
        all_pkgs = self.__get_appliance_linux_packages()
        if all_pkgs is not None and hasattr(all_pkgs, "pkgs"):
            table.add_row(["# OS Packages", str(len(all_pkgs.pkgs.pkg))])
            table.add_row(["Packages Total Size", size(self.appliance.osProfile.size)])

            if self.print_details:
                pkg_number = 0
                all_pkgs = generics_utils.order_list_object_by(all_pkgs.pkgs.pkg, "name")
                for index, pkg in enumerate(all_pkgs, start=1):
                    table.add_row(self.__prepare_linux_pkg_os_profile(pkg, pkg_number))
                    pkg_number += 1

    def __prepare_linux_pkg_os_profile(self, pkg, pkg_number):
        return ["Packages #" + str(pkg_number),
                pkg.name + " " + pkg.version + " " + pkg.arch + " (" + size(pkg.size) + ")"]

    def __get_appliance_linux_packages(self):
        packages_uri = extractId(self.appliance.osProfile.packagesUri, operation=False)
        all_pkgs = self.api.Users(self.user_account).Appliances(packages_uri[1]).Osprofile(
            packages_uri[0]).Pkgs.Getall()
        return all_pkgs

    def print_projects(self):
        printer.out("Projects", printer.INFO)
        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])

        all_projects = self.api.Users(self.user_account).Appliances(self.appliance.dbId).Projects.Getall()
        if all_projects:
            nb_of_projects = len(all_projects.projects.project)
        else:
            nb_of_projects = 0

        table.add_row(["# Projects", str(nb_of_projects)])

        if self.print_details and nb_of_projects != 0:
            project_number = 0
            for index, project in enumerate(all_projects.projects.project, start=1):
                table.add_row(["Project #" + str(project_number),
                               project.name + " " + project.version + " (" + project.size + " bytes)"])
        print table.draw() + "\n"

    def print_software(self):
        printer.out("My Software", printer.INFO)
        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])

        all_software = self.api.Users(self.user_account).Appliances(self.appliance.dbId).Mysoftware.Getall()

        if all_software:
            nb_of_software = len(all_software.mySoftwareList.mySoftware)
        else:
            nb_of_software = 0
        table.add_row(["# Custom Software", nb_of_software])

        if self.print_details and nb_of_software != 0:
            software_number = 0
            for index, software in enumerate(all_software.mySoftwareList.mySoftware, start=1):
                table.add_row(["Software #" + str(software_number),
                               software.name + " " + software.version + " (" + software.size + " bytes)"])
        print table.draw() + "\n"

    def print_configuration(self):
        printer.out("Configuration", printer.INFO)
        table = init_texttable(None, 200, ["l", "l"], ["a", "t"])

        self.__prepare_oas_packages(table)
        self.__prepare_boot_scripts(table)

        print table.draw() + "\n"

    def __prepare_boot_scripts(self, table):
        if self.appliance.bootScriptsUri is None:
            table.add_row(["# Boot Scripts", "0"])
        else:
            boot_scripts = self.api.Users(self.user_account).Appliances(self.appliance.dbId).Bootscripts(
                extractId(self.appliance.bootScriptsUri)).Getall()

            table.add_row(["# Boot Scripts", str(len(boot_scripts.bootScripts.bootScript))])

            boot_scripts_number = 0
            for index, item in enumerate(boot_scripts.bootScripts.bootScript, start=1):
                table.add_row(
                    ["Boot Script #" + str(boot_scripts_number) + " details", item.name + " " + item.bootType])

    def __prepare_oas_packages(self, table):
        if self.appliance.oasPackageUri is None:
            table.add_row(["OAS Pkg Uploaded", "No"])
        else:
            oas = self.api.Users(self.user_account).Appliances(self.appliance.dbId).Oas(
                extractId(self.appliance.oasPackageUri)).Get()

            if not oas.uploaded:
                table.add_row(["OAS Pkg Uploaded", "No"])
            else:
                table.add_row(["OAS Pkg Uploaded", "Yes"])
                table.add_row(["OAS Pkg", oas.name])
                table.add_row(["OAS Pkg Size", size(oas.size)])
                if oas.licenseUploaded:
                    table.add_row(["OAS Licence Uploaded", "Yes"])
                else:
                    table.add_row(["OAS Licence Uploaded", "No"])
