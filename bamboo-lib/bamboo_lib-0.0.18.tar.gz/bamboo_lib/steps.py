import re
import zipfile

from bamboo_lib.helpers import grab_connector, random_char
from bamboo_lib.models import PipelineStep, ResultWrapper
from bamboo_lib.logger import logger

class DownloadStep(PipelineStep):
    def __init__(self, connector=None, connector_path=None, callback=None):
        if not connector:
            raise ValueError("Must specify a connector")
        if isinstance(connector, str):
            cpath = connector_path or __file__
            self.connector = grab_connector(cpath, connector)
        else:
            self.connector = connector
        self.callback = callback

    def run_step(self, prev, params):
        logger.debug("DOWNLOAD STEP")
        # Download Cube (URL defined in conns.yaml file.)
        # This step will save the contents of the connector target
        # to a file and then pass a file path to the next step
        return self.connector.download(params=params, callback=self.callback)

class LoadStep(PipelineStep):
    OPTIONS = ["if_exists", "schema", "index", "index_label", "chunksize", "dtype", "pk", "table_schema_only", "data_only", "connector_path", "nullable_list"]

    def __init__(self, table_name, connector, **kwargs):
        self.table_name = table_name
        if isinstance(connector, str):
            cpath = kwargs.get("connector_path", None) or __file__
            self.connector = grab_connector(cpath, connector)
            if "connector_path" in kwargs:
                del kwargs["connector_path"]
        else:
            self.connector = connector
        for key, val in kwargs.items():
            if key in LoadStep.OPTIONS:
                setattr(self, key, val)
            else:
                raise ValueError("Invalid parameter", key, val)

    def run_step(self, prev, params):
        logger.info("Running LoadStep step...")
        df = prev
        kwargs = {key: getattr(self, key) for key in self.OPTIONS if hasattr(self, key)}
        self.connector.write_df(self.table_name, df, **kwargs)
        return prev


class LoadStepDynamic(PipelineStep):
    OPTIONS = ["if_exists", "schema", "index", "index_label", "chunksize", "dtype", "pk"]

    def __init__(self, df_key, table_name_key, connector, **kwargs):
        self.df_key = df_key
        self.table_name_key = table_name_key
        self.connector = connector
        for key, val in kwargs.items():
            if key in LoadStep.OPTIONS:
                setattr(self, key, val)
            else:
                raise ValueError("Invalid parameter", key, val)

    def run_step(self, prev, params):
        logger.info("Running LoadStep step...")
        df = prev.get(self.df_key)
        kwargs = {key: getattr(self, key) for key in self.OPTIONS if hasattr(self, key)}
        self.connector.write_df(prev.get(self.table_name_key), df, **kwargs)
        return prev


class UnzipStep(PipelineStep):
    def __init__(self, compression='zip', pattern=None):
        self.compression = compression
        supported_compression = ['zip']
        self.pattern = pattern
        if self.compression not in supported_compression:
            raise Exception("extension not supported!")

    def run_step(self, filepath, params):
        if self.compression == 'zip':
            zfile = zipfile.ZipFile(filepath)
            for finfo in zfile.infolist():
                if not self.pattern or re.search(self.pattern, finfo.filename):
                    yield zfile.open(finfo)

        # return compressor(full_path)


class WriteDFToDiskStep(PipelineStep):
    def __init__(self, target_path, compression=None):
        self.target_path = target_path
        self.compression = compression

    def run_step(self, df, params):
        df.to_csv(self.target_path, index=False, compression=self.compression)
        return self.target_path


class SCPTransferStep(PipelineStep):
    def __init__(self, target_path, connector, **kwargs):
        if not target_path or not connector:
            raise Exception("You must specify a target path and a connector")
        super(SCPTransferStep, self).__init__(**kwargs)
        self.target_path = target_path
        self.connector = connector

    def run_step(self, file_obj, params):
        logger.debug("Transfering schema file: {} ...".format(self.target_path))
        use_fo = not isinstance(file_obj, str)
        self.connector.send_file(file_obj, self.target_path, use_fo=use_fo)
        logger.debug("Transfer complete!")
        return True


class SSHCommandStep(PipelineStep):
    def __init__(self, cmd, connector, **kwargs):
        if not cmd or not connector:
            raise Exception("You must specify a target path and a connector")
        super(SSHCommandStep, self).__init__(**kwargs)
        self.cmd = cmd
        self.connector = connector

    def run_step(self, input, params):
        logger.debug("Running command on remote host: {} ...".format(self.cmd))
        # self.connector.send_file(file_obj, self.target_path, use_fo=True)
        output = self.connector.run_command(self.cmd)
        logger.debug("Command complete! Result was:\n\n {}\n\n".format(output))
        return ResultWrapper(previous_result=input, current_result=output)


class LockStep(PipelineStep):
    def __init__(self, lock_name, redis_connector, next_step):
        import sherlock  # -- only use if needed
        sherlock.configure(timeout=45, backend=sherlock.backends.REDIS, client=redis_connector.get_client())
        self.lock_name = lock_name
        self.lock = sherlock.Lock(lock_name)
        self.next_step = next_step

    def run_step(self, prev, params):
        logger.debug("Waiting for lock {} ...".format(self.lock_name))
        self.lock.acquire()
        logger.debug("Acquired lock {} ...".format(self.lock_name))
        logger.debug("Running step...")
        result = self.next_step.run_step(prev, params)
        self.lock.release()
        logger.debug("Lock released!")
        return result


class SSHTunnelStartStep(PipelineStep):
    def __init__(self, sshtunnel_connector):
        self.sshtunnel_connector = sshtunnel_connector

    def run_step(self, prev, params):
        self.sshtunnel_connector.start()
        return prev


class SSHTunnelCloseStep(PipelineStep):
    def __init__(self, sshtunnel_connector):
        self.sshtunnel_connector = sshtunnel_connector

    def run_step(self, prev, params):
        self.sshtunnel_connector.close()
        return prev


class IngestMonetStep(PipelineStep):
    def __init__(self, table_name, schema, db_name, conns_path, compression=None):
        self.table_name = table_name
        self.schema = schema
        self.db_name = db_name
        self.conns_path = conns_path
        self.compression = compression

    def run_step(self, prev, params):
        # connectors config
        server_str = params.get("server-connector")
        sftp_connector = grab_connector(self.conns_path, server_str)

        monet_connector = grab_connector(self.conns_path, "monet-remote")
        redis_connector = grab_connector(self.conns_path, "redis-remote")

        lock_name = params.get("lock_name", "monet-lock")

        # prep csv file for write to disk and transfer to server
        # (including compression)
        random_filename = random_char(32)
        target_path = "/tmp/{}-{}.csv".format(self.schema, random_filename)
        if self.compression == "gzip":
            target_path = target_path + ".gz"
        elif self.compression == "bz2":
            target_path = target_path + ".bz2"

        write_to_disk_step = WriteDFToDiskStep(target_path=target_path, compression=self.compression)
        transfer_step = SCPTransferStep(target_path, sftp_connector)

        # Create table
        # Must use lock because Monetdb does not support table creation concurrent
        # with any other transaction (including COPY)
        # put the table gen into a load step which is wrapped by the lock step
        # for ssh tunnel, just have to start one manually, and then latch onto it with
        # the ssh_tunnel step by specifying the port.
        # e.g. ssh -L 6379:localhost:6379 deploy@canon -N

        create_table_step = LoadStep(self.table_name, monet_connector, table_schema_only=True, schema=self.schema)
        create_table_with_lock_step = LockStep(lock_name, redis_connector, create_table_step)

        # Ingest
        ingest_cmd = '''mclient -d {} -h localhost -s "COPY OFFSET 2 INTO {}.{} FROM '{}' USING DELIMITERS ',', '\n', '\\\"' NULL AS '' "'''.format(self.db_name, self.schema, self.table_name, target_path)
        remote_cmd_step = SSHCommandStep(ingest_cmd, sftp_connector)

        # Run steps
        res_1 = create_table_with_lock_step.run_step(prev, params)
        res_2 = write_to_disk_step.run_step(res_1, params)
        res_3 = transfer_step.run_step(res_2, params)
        res_4 = remote_cmd_step.run_step(res_3, params)

        return res_4


class BaseGenerateSchemaStep(PipelineStep):
    """ This step serves as a base for generating dynamic schemas. It consists
    of helper methods to generate elements to populate template XML files which
    are then output into a <cube>.xml in a desired location.
    The following is an outline of the basic structure currently supported:

    - Cube
      - Annotation(s)
      - Dimension(s)
        - Annotation(s)
        - Hierarchy(s)
          - Table
          - Level(s)
      - Measure(s)
    """

    @staticmethod
    def create_annotation(name, value):
        """ Creates an Annotation object. After passing through the template
        builder, the output will look like:

        <Annotation name="title">Title</Annotation>

        :param name: name of this annotation
        :param value: value for this annotation
        :return: Annotation object
        """
        return {
            "name": name,
            "value": value
        }

    @staticmethod
    def create_dimension(name, hierarchies, foreign_key="", annotations=None):
        """ Creates a Dimension object. After passing through the template
        builder, the output will look like:

        <Dimension foreignKey="region_id" name="Region">
            ... Annotations and Hierarchies can go in here ...
        </Dimension>

        :param name: name of this dimension
        :param hierarchies: list of hierarchies for this dimension
        :param foreign_key: name of column in the fact table used to connect to
                            a dimension table
        :param annotations: list of annotations
        :return: Dimension object
        """
        if not isinstance(hierarchies, list):
            raise TypeError("'hierarchies' should be a list")
        if annotations and not isinstance(annotations, list):
            raise TypeError("'annotations' should be a list")

        return {
            "name": name, "foreign_key": foreign_key, "annotations": annotations,
            "hierarchies": hierarchies
        }

    @staticmethod
    def create_hierarchy(table, levels, name="", primary_key="", has_all=""):
        """ Creates a Hierarchy object. After passing through the template
        builder, the output will look like:

        <Hierarchy name="City" primaryKey="geoid" hasAll="true">
            ... Table and Levels will be rendered here ...
        </Hierarchy>

        :param table: dimension table for this hierarchy
        :param levels: levels of this hierarchy
        :param name: name of this hierarchy
        :param primary_key: primary key in the dimension table
        :param has_all: whether the hierarchy should have an 'All' level
        :return: Hierarchy object
        """
        if not isinstance(table, dict):
            raise TypeError("'table' should be a dict")
        if not isinstance(levels, list):
            raise TypeError("'levels' should be a list")

        return {
            "table": table, "levels": levels, "name": name,
            "has_all": has_all, "primary_key": primary_key,
        }

    @staticmethod
    def create_table(name, schema):
        """ Creates a Table object. After passing through the template
        builder, the output will look like:

        <Table name="sales" schema="store_sales" />

        :param name: name of this table
        :param schema: schema where the table is located
        :return: Table object
        """
        return {"name": name, "schema": schema}

    @staticmethod
    def create_level(name, column, _type="", level_type="", name_column="",
                     unique_members=""):
        """ Creates a Level object. After passing through the template
        builder, the output will look like:

        <Level name="Year" column="year" type="Numeric" levelType="TimeYears"
               nameColumn="year_name" uniqueMembers="true" />

        :param name: name of this level
        :param column: column in the dimension table corresponding to this level
        :param _type:
        :param level_type:
        :param name_column: name column in the dimension table for this level
        :param unique_members: whether the members of this
        :return: Level object
        """
        return {
            "name": name, "column": column, "type": _type,
            "level_type": level_type, "name_column": name_column,
            "unique_members": unique_members
        }

    @staticmethod
    def create_measure(name, column, aggregator):
        """ Creates a Measure object. After passing through the template
        builder, the output will look like:

        <Measure name="Imports" column="imports" aggregator="sum" />

        :param name: name of this measure
        :param column: column in the fact table corresponding to this measure
        :param aggregator: aggregator for this measure
        :return: Measure object
        """
        return {"name": name, "column": column, "aggregator": aggregator}

    @staticmethod
    def write_cube_file(cube_name, table_name, schema_name, annotations,
                        dimensions, measures, file_location, file_name):
        """ Writes a cube XML file into a desired location using the `cube.xml`
        template.

        :param cube_name: name of the cube being created
        :param table_name: name of the fact table for this cube
        :param schema_name: name of the schema where the fact table is located
        :param annotations: list of annotations
        :param dimensions: list of dimensions
        :param measures: list of measures
        :param file_location: folder where the file should be written
        :param file_name: name of the file
        :return template: the template generated
        """
        env = Environment(
            loader=PackageLoader("bamboo_lib", "templates"),
            autoescape=select_autoescape(["xml"])
        )

        template = env.get_template("cube.xml")
        template = template.render(
            cube_name=cube_name,
            table_name=table_name,
            schema_name=schema_name,
            annotations=annotations,
            dimensions=dimensions,
            measures=measures
        )

        with open("%s/%s.xml" % (file_location, file_name), "w") as f:
            f.write(template)

        return template
