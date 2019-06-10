class TestBedOptions:
    def __init__(self, dictionary):
        # clientId, kafkaHost, schemaRegistry)
        # Unique ID of this client
        self.client_id = None

        # Uri for the Kafka broker, e.g. broker:3501
        self.kafka_host = None

        # Uri for the schema registry, e.g. schema_registry:3502
        self.schema_registry = "localhost:3502"

        # If true, automatically register schema's on startup
        self.auto_register_schemas = False

        # If autoRegisterSchemas is true, contains the folder with *.avsc schema's to register
        self.schema_folder = "data/schemas/"

        # If true fetch all schema versions (and not only the latest)
        self.fetch_all_versions = False

        # If true fetch all schema's (and not only the consume and produce topics)
        self.fetch_all_schemas = False

        # If true fetch all schema's (and not only the consume and produce topics)
        self.fetch_all_topics = False

        # If set true, use the topics offset to retreive messages
        self.exclude_internal_topics = False

        # Reset the offset messages on start.
        self.reset_offset_on_start = False

        # Offset type possibles: LATEST, EARLIEST
        self.offset_type = "EARLIEST"

        # How often should the adapter try to reconnect to the kafka server if the first time fails
        self.reconnection_retries = 5

        # Interval between two heartbeat messages in secs
        self.heartbeat_interval = 0.1

        # Send messages asynchronously
        self.send_messages_asynchronously = True

        # Topics you want to consume
        self.consume = []

        # Topics you want to produce
        self.produce = []

        # If set true, use SSL
        self.use_ssl = False

        # Path to trusted CA certificate. It will only be used if use_ssl is set true.
        self.ca_file = ""

        # Path to client certificate. It will only be used if use_ssl is set true.
        self.cert_file: str = None

        # Path to client private-key file. It will only be used if use_ssl is set true.
        self.key_file: str = None

        # Password for private key. It will only be used if use_ssl is set true.
        self.password_private_key: str = None


        # Here we override the default values if they were introduced in the dictionary as an input of the constructor
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def validate_options(self):
        print("")

    def get_options_from_file(self):
        print("")
        
        
