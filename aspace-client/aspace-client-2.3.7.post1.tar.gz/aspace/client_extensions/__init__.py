r"""
This module contains classes that leverage existing endpoints of the 
ArchivesSpace API to extend its functionality. Examples of the types
of utilities included in this package are

- Streaming Records 1 by 1 from the API, using the `all_ids` flag.
- Providing paging controls for GET endpoints that support paging.
- Updating user passwords.

These components can be accessed through the ASpaceClient class.
"""

import aspace.client_extensions.record_streams
import aspace.client_extensions.user_management
import aspace.client_extensions.enum_management
import aspace.client_extensions.schema_query
import aspace.client_extensions.jobs
import aspace.client_extensions.top_containers
