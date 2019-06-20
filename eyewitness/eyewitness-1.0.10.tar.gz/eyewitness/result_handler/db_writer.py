import sqlite3
import logging

from eyewitness.config import BBOX, FEEDBACK_NO_OBJ
from eyewitness.detection_utils import DetectionResultHandler
from eyewitness.audience_id import AudienceRegister
from eyewitness.feedback_msg_utils import FeedbackMsgHandler
from eyewitness.image_id import ImageRegister
from eyewitness.models import detection_models
from eyewitness.models import feedback_models
from eyewitness.models.db_proxy import DATABASE_PROXY

LOG = logging.getLogger(__name__)


class BboxNativeSQLiteDbWriter(DetectionResultHandler, ImageRegister):
    def __init__(self, db_path):
        """
        Parameters
        ----------
        db_path: str
            database path
        """
        self.conn = sqlite3.connect(db_path)
        self.create_db_table()

    @property
    def detection_method(self):
        """str: BBOX"""
        return BBOX

    def _handle(self, detection_result):
        """
        handle detection result

        Parameters
        ----------
        detection_result: DetectionResult
            detection result
        """
        image_id = detection_result.image_id
        self.insert_detection_objs(
            str(image_id), detection_result.detected_objects)
        if detection_result.drawn_image_path:
            self.update_image_drawn_image_path(image_id, detection_result.drawn_image_path)

    def create_db_table(self):
        """
        create ImageInfo, BboxDetectionResult table if table not exist
        """
        print('connet/create image_info table')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS ImageInfo(
                          image_id TEXT PRIMARY KEY,
                          timestamp INTEGER,
                          channel TEXT,
                          file_format TEXT,
                          raw_image_path TEXT,
                          drawn_image_path TEXT
                          )''')

        print('connet/create bbox_detection_results table')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS BboxDetectionResult(
                          ID INTEGER PRIMARY KEY AUTOINCREMENT,
                          image_id TEXT,
                          x1 INTEGER,
                          y1 INTEGER,
                          x2 INTEGER,
                          y2 INTEGER,
                          label TEXT,
                          score REAL,
                          meta TEXT,
                          FOREIGN KEY(image_id) REFERENCES image_info(image_id)
                          )''')
        self.conn.commit()

    def insert_image_info(self, image_id, raw_image_path=None):
        """
        insert image_info which used for unit-test

        Parameters
        ----------
        image_id: str
            image_id
        raw_image_path: str
             the path of raw image stored
        """
        try:
            timestamp = image_id.timestamp
            channel = image_id.channel
            file_format = image_id.file_format
            self.conn.execute('''INSERT INTO ImageInfo(image_id, timestamp, channel, file_format,
                              raw_image_path) VALUES(?,?,?,?,?)''',
                              (str(image_id), timestamp, channel, file_format, raw_image_path))
            self.conn.commit()
        except Exception:
            LOG.warn('register image %s failure', image_id)
            pass

    def update_image_drawn_image_path(self, image_id, drawn_image_path):
        """
        update db image_id.drawn_image_path
        """
        try:
            self.conn.execute('''UPDATE ImageInfo SET drawn_image_path = ? where image_id = ? ''',
                              (drawn_image_path, str(image_id)))
            self.conn.commit()
        except ValueError:
            print("update failure")
            pass

    def insert_detection_objs(self, image_id, detected_objects):
        """
        insert detection results into db.

        Parameters
        ----------
        image_id: str
            image_id
        detected_objects: List[BoundedBoxObject]
            detected objects
        """
        try:
            for detected_obj in detected_objects:
                left, top, right, bottom, label, score, meta = detected_obj
                self.conn.execute(
                    '''INSERT INTO BboxDetectionResult
                       (image_id, x1, y1, x2, y2, label, score, meta)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (image_id, left, top, right, bottom, label, score, meta))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass


class BboxPeeweeDbWriter(DetectionResultHandler, ImageRegister):
    def __init__(self, database, auto_image_registration=False):
        """
        Parameters
        ----------
        database: peewee.Database
            peewee db obj

        auto_image_registration: Bool
            enable the auto_image_registration will check if image registered or not
            which might make the handle function more slowly
        """
        # setup database for models
        self.database = database
        DATABASE_PROXY.initialize(self.database)
        self.create_db_table()
        self.auto_image_registration = auto_image_registration

    @property
    def detection_method(self):
        return BBOX

    def check_proxy_db(self):
        """check if the db proxy is correct one, if not initialize again.
        """
        if not (self.database is DATABASE_PROXY.obj):
            DATABASE_PROXY.initialize(self.database)

    def _handle(self, detection_result):
        """
        Parameters
        ----------
        detection_result: DetectionResult
            detection_result
        """
        image_id = detection_result.image_id

        if self.auto_image_registration:
            query = detection_models.ImageInfo.select().where(
                detection_models.ImageInfo.image_id == image_id)
            if not query.exists():
                LOG.info('image_info: %s not exist, register it.', image_id)
                self.insert_image_info(image_id)

        self.insert_detection_objs(
            image_id, detection_result.detected_objects)

        if detection_result.drawn_image_path:
            self.update_image_drawn_image_path(image_id, detection_result.drawn_image_path)

    def create_db_table(self):
        """
        create ImageInfo, BboxDetectionResult table if table not exist
        """
        detection_models.ImageInfo.create_table()
        detection_models.BboxDetectionResult.create_table()

    def insert_image_info(self, image_id, raw_image_path=None):
        """
        insert image_info which used for unit-test

        Parameters
        ----------
        image_id: ImageId obj
            image_id obj (including  channel, timestamp, file-format)
        raw_image_path: str
            the path of raw image stored
        """
        try:
            self.check_proxy_db()
            timestamp = image_id.timestamp
            channel = image_id.channel
            file_format = image_id.file_format
            image_info = detection_models.ImageInfo(
                image_id=str(image_id), timestamp=timestamp, channel=channel,
                file_format=file_format, raw_image_path=raw_image_path)
            # according to document:
            # http://docs.peewee-orm.com/en/latest/peewee/models.html#non-integer-primary-keys-composite-keys-and-other-tricks
            # model with Non-integer primary keys need to pass `force_insert=True`
            image_info.save(force_insert=True)
        except ValueError:
            LOG.warn('register image %s failure', image_id)
            pass

    def update_image_drawn_image_path(self, image_id, drawn_image_path):
        """
        update db image_id.drawn_image_path
        """
        try:
            self.check_proxy_db()
            image_info = detection_models.ImageInfo(
                image_id=str(image_id), drawn_image_path=drawn_image_path)
            image_info.save(only=[detection_models.ImageInfo.drawn_image_path])
        except ValueError:
            pass

    def insert_detection_objs(self, image_id, detected_objects):
        """
        insert detection results into db.

        Parameters
        ----------
        image_id: str
            image_id
        detected_objects: List[BoundedBoxObject]
            detected objects
        """
        try:
            self.check_proxy_db()
            for detected_obj in detected_objects:
                left, top, right, bottom, label, score, meta = detected_obj
                detection_result = detection_models.BboxDetectionResult(
                    image_id=image_id, x1=left, y1=top, x2=right, y2=bottom, label=label,
                    score=score, meta=meta)
                detection_result.save()
        except ValueError:
            pass


class FalseAlertPeeweeDbWriter(FeedbackMsgHandler, AudienceRegister, ImageRegister):
    def __init__(self, database):
        """
        Parameters
        ----------
        database: peewee.Database
            peewee db obj
        """
        # setup database for models
        self.database = database
        DATABASE_PROXY.initialize(self.database)
        self.create_db_table()

    @property
    def feedback_method(self):
        return FEEDBACK_NO_OBJ

    def check_proxy_db(self):
        """check if the db proxy is correct one, if not initialize again.
        """
        if not (self.database is DATABASE_PROXY.obj):
            DATABASE_PROXY.initialize(self.database)

    def _handle(self, feedback_msg):
        """
        Parameters
        ----------
        feedback_msg: FeedbackMsg
            feedback_msg
        """
        self.insert_feedback_obj(feedback_msg)

    def create_db_table(self):
        """
        create ImageInfo, RegisteredAudience, FalseAlertFeedback table if table not exist
        """
        detection_models.ImageInfo.create_table()
        feedback_models.RegisteredAudience.create_table()
        feedback_models.FalseAlertFeedback.create_table()

    def insert_image_info(self, image_id, raw_image_path=None):
        """
        insert image_info which used for unit-test

        Parameters
        ----------
        image_id: str
            image_id
        raw_image_path: str
            the path of raw image stored
        """
        try:
            self.check_proxy_db()
            timestamp = image_id.timestamp
            channel = image_id.channel
            file_format = image_id.file_format
            image_info = detection_models.ImageInfo(
                image_id=str(image_id), timestamp=timestamp, channel=channel,
                file_format=file_format, raw_image_path=raw_image_path)
            # according to document:
            # http://docs.peewee-orm.com/en/latest/peewee/models.html#non-integer-primary-keys-composite-keys-and-other-tricks
            # model with Non-integer primary keys need to pass `force_insert=True`
            image_info.save(force_insert=True)
        except ValueError:
            LOG.warn('register image %s failure', image_id)
            pass

    def insert_registered_user(self, audience_id, register_time, description):
        """
        insert image_info which used for unit-test

        Parameters
        ----------
        audience_id: AudienceId

        register_time: int

        description: str
        """
        try:
            platform_id = audience_id.platform_id
            user_id = audience_id.user_id
            self.check_proxy_db()
            user_to_register = feedback_models.RegisteredAudience(
                audience_id=str(audience_id), user_id=user_id,
                platform_id=platform_id, register_time=register_time,
                description=description)
            # according to document:
            # http://docs.peewee-orm.com/en/latest/peewee/models.html#non-integer-primary-keys-composite-keys-and-other-tricks
            # model with Non-integer primary keys need to pass `force_insert=True`
            user_to_register.save(force_insert=True)
        except ValueError:
            pass

    def insert_feedback_obj(self, feedback_msg):
        """
        insert feedback obj into db.

        Parameters
        ----------
        feedback_msg: FeedbackMsg
        """
        try:
            audience_id = feedback_msg.audience_id
            user_id = audience_id.user_id
            platform_id = audience_id.platform_id
            image_id = feedback_msg.image_id
            receive_time = feedback_msg.receive_time
            feedback_meta = feedback_msg.feedback_meta
            is_false_alert = feedback_msg.is_false_alert

            self.check_proxy_db()
            feedback_model_obj = feedback_models.FalseAlertFeedback(
                audience_id=str(audience_id), user_id=user_id, platform_id=platform_id,
                image_id=str(image_id), receive_time=receive_time, feedback_meta=feedback_meta,
                is_false_alert=is_false_alert)

            feedback_model_obj.save()
        except ValueError:
            pass
