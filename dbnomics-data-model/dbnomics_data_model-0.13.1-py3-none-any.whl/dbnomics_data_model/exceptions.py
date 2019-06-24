# dbnomics-data-model -- Define, validate and transform DBnomics data.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2017-2018 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-data-model
#
# dbnomics-data-model is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-data-model is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


class DBnomicsError(Exception):
    pass


class StorageError(DBnomicsError):
    """Problem while accessing the storage of DBnomics data."""

    def __init__(self, base_message, provider_code=None, dataset_code=None, series_code=None):
        self.base_message = base_message
        self.provider_code = provider_code
        self.dataset_code = dataset_code
        self.series_code = series_code
        super().__init__(self.message)

    @property
    def message(self):
        if self.provider_code is not None and self.dataset_code is not None and self.series_code is not None:
            details = " for series \"{}/{}/{}\"".format(self.provider_code, self.dataset_code, self.series_code)
        elif self.provider_code is not None and self.dataset_code is not None:
            details = " for dataset \"{}/{}\"".format(self.provider_code, self.dataset_code)
        elif self.provider_code is not None:
            details = " for provider \"{}\"".format(self.provider_code)
        else:
            details = ""
        return self.base_message + details
