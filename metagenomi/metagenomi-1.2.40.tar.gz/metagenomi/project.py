import time
import threading
import queue
from boto3.dynamodb.conditions import Key, Attr

from metagenomi.logger import logger
from metagenomi.db import dbconn
from metagenomi.models.assembly import Assembly
from metagenomi.models.sequencing import Sequencing
from metagenomi.models.sample import Sample
from metagenomi.base import MgObj


class MgProject:
    '''
    A representation of a lot of MgObjects
    '''

    def __init__(self, mgproject='ALL', db=dbconn, check=False, derive_associations=False, load=True):
        self.db = db
        self.check = check

        # if isinstance(mgproject, list):
        # mgproject can be a list
        self.mgproject = mgproject
        self.sequencings = []
        self.assemblies = []
        self.samples = []
        self.association_map = {}
        self.items = None

        if load:
            self.load()

        if derive_associations:
            self.derive_associations()

    def load(self, check=False):
        if self.mgproject == 'ALL':
            items = self.parallel_scan()
        else:
            items = self.query(self.mgproject)

        assemblies = [i for i in items if i['mgtype'] == 'assembly']
        self.assemblies = [Assembly(db=self.db, check=self.check, **i)
                           for i in assemblies]

        sequencings = [i for i in items if i['mgtype'] == 'sequencing']
        self.sequencings = [Sequencing(db=self.db, check=self.check, **i)
                            for i in sequencings]

        samples = [i for i in items if i['mgtype'] == 'sample']
        self.samples = [Sample(db=self.db, check=self.check, **i)
                        for i in samples]

    def load_assemblies(self, check=False):
        start = time.time()
        if self.mgproject == 'ALL':
            items = self.query('assembly', index='mgtype-index', key='mgtype')
        else:
            if self.items is None:
                self.items = self.query(self.mgproject)
            items = self.items

        assemblies = [i for i in items if i['mgtype'] == 'assembly']
        self.assemblies = [Assembly(db=self.db, check=self.check, **i)
                           for i in assemblies]
        end = time.time()
        m = f'Loaded {len(self.assemblies)} assemblies in {end-start} seconds'
        print(m)
        logger.info(m)

    def load_sequencings(self, check=False):
        '''
        Make it so that not everything is reloaded
        '''
        start = time.time()
        if self.mgproject == 'ALL':
            items = self.query('sequencing', index='mgtype-index', key='mgtype')
        else:
            if self.items is None:
                self.items = self.query(self.mgproject)
            items = self.items

        sequencings = [i for i in items if i['mgtype'] == 'sequencing']
        self.sequencings = [Sequencing(db=self.db, check=self.check, **i)
                            for i in sequencings]
        end = time.time()
        m = f'Loaded {len(self.sequencings)} sequencings in {end-start} seconds'
        print(m)
        logger.info(m)

    def load_samples(self, check=False):
        start = time.time()
        if self.mgproject == 'ALL':
            print('querying all samples')
            items = self.query('sample', index='mgtype-index', key='mgtype')
        else:
            if self.items is None:
                self.items = self.query(self.mgproject)
            items = self.items

        self.samples = [Sample(db=self.db, check=self.check, **i)
                        for i in items if i['mgtype'] == 'sample']
        end = time.time()
        m = f'Loaded {len(self.samples)} samples in {end-start} seconds'
        print(m)
        logger.info(m)

    def query(self, value, index='mgproject-mgtype-index', key='mgproject'):
        """
        Queries the database given a value, index, and key.
        First selects the index, and then returns all items (in a pageinated
        fasion where Key(key).eq(value).
        """
        print('Querying the database')

        # If multiple projects given
        if isinstance(value, list):
            items = []
            for v in value:
                items += self.query(v, index=index, key=key)
            return items

        else:
            response = self.db.table.query(
                IndexName=index,
                KeyConditionExpression=Key(key).eq(value)
                )

            items = response['Items']
            while True:
                print(f'Loaded {len(items)} items')
                if response.get('LastEvaluatedKey'):
                    response = self.db.table.query(
                        IndexName=index,
                        KeyConditionExpression=Key(key).eq(value),
                        ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                    items += response['Items']
                else:
                    break

            return items

    def process_segment(self, segment=0, total_segments=10):
        # We pass in the segment & total_segments to scan here.
        response = self.db.table.scan(Segment=segment, TotalSegments=total_segments)

        items = response['Items']
        while True:
            print(f'Loaded {len(items)} items')
            if response.get('LastEvaluatedKey'):
                response = self.db.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    Segment=segment,
                    TotalSegments=total_segments
                    )
                items += response['Items']
            else:
                break

        print(f'found {len(items)} items')
        self.parallel_scan_items[segment] = items

    def parallel_scan(self):
        start = time.time()
        self.parallel_scan_items = {}
        pool = []
        pool_size = 100

        for i in range(pool_size):
            worker = threading.Thread(
                target=self.process_segment,
                kwargs={
                    'segment': i,
                    'total_segments': pool_size,
                }
            )
            pool.append(worker)
            # We start them to let them start scanning & consuming their
            # assigned segment.
            worker.start()

        # Finally, we wait for each to finish.
        for thread in pool:
            # print(thread)
            thread.join()

        final_items = []
        for k, v in self.parallel_scan_items.items():
            final_items += v

        end = time.time()
        print(f'scanned {len(final_items)} in {end-start}')
        return final_items

    def scan(self, filter_key=None, filter_value=None, comparison='equals'):
        """
        not currently in use
        """
        start = time.time()
        if filter_key and filter_value:
            if comparison == 'equals':
                filtering_exp = Key(filter_key).eq(filter_value)
            elif comparison == 'contains':
                filtering_exp = Attr(filter_key).contains(filter_value)

            response = self.db.table.scan(
                FilterExpression=filtering_exp)

            items = response['Items']
            while True:
                print(f'Loaded {len(items)} items')
                if response.get('LastEvaluatedKey'):
                    response = self.db.table.scan(
                        ExclusiveStartKey=response['LastEvaluatedKey'],
                        FilterExpression=filtering_exp
                        )
                    items += response['Items']
                else:
                    break

            return items

        else:
            response = self.db.table.scan()

            items = response['Items']
            while True:
                print(f'Loaded {len(items)} items')
                if response.get('LastEvaluatedKey'):
                    response = self.db.table.scan(
                        ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                    items += response['Items']
                else:
                    break

            end = time.time()
            print(f'Scanned {len(items)} items in {end-start} time')
            return items

    def derive_associations(self):
        '''
        TODO: This only checks that everything is in the project. It does not
        check for one-way links. i.e. if Assembly --> Seq but Seq !--> Assembly
        '''
        for mgobj in self.assemblies + self.samples + self.sequencings:
            # print('Working on: ', mgobj.mgid)
            for type, mgobj_list in mgobj.associated.items():
                for o in mgobj_list:
                    if not o == 'None':
                        # print(o)
                        connection = self.find_object(o)
                        # if mgobj.mgtype == 'assembly':

                        if mgobj in self.association_map:
                            self.association_map[
                                mgobj
                                ] = self.association_map[mgobj] + [connection]
                        else:
                            self.association_map[mgobj] = [connection]

    def get_undone_downloads(self, load=True):
        if load:
            self.load_sequencings()

        undone = []
        running = []
        for i in self.sequencings:
            if i.sequencing_info is None:
                undone.append(i)
            else:
                if 'test' in i.s3path:
                    print(i.mgid)
                    if i.sequencing_info.get_job_status() == 'RUNNING':
                        running.append(i)
                    else:
                        undone.append(i)

        print({'undone': len(undone), 'running': len(running)})
        return(undone, running)

    # def get_completed_downloads(self, load=True):
    #     if load:
    #         self.load_sequencings()
    #
    #     undone = []
    #     running = []
    #     for i in self.sequencings:
    #         if i.sequencing_info is None:
    #             undone.append(i)
    #         else:
    #             if 'test' in i.s3path:
    #                 print(i.mgid)
    #                 if i.sequencing_info.get_job_status() == 'RUNNING':
    #                     running.append(i)
    #                 else:
    #                     undone.append(i)
    #
    #     print({'undone': len(undone), 'running': len(running)})
    #     return(undone, running)

    def find_object(self, o, raise_error=True):
        '''
        Given the mgid of an object, return the instance of that object.
        TODO: Test speed of this function
        '''
        # print(f'Finding {o}')
        if isinstance(o, MgObj):
            print('is instance')
            return o

        for i in self.assemblies + self.samples + self.sequencings:
            if i.mgid == o:
                return i
        if raise_error:
            raise ValueError(f'Object {o} is not in this project')
        else:
            return None

    def count_bps(self, as_df=True):
        # 4 million bases per G zipped file size_mb
        # 4905611824 bp in 2710 MB size file
        # UPDATED: 1.8 million base pairs per 1 MB file size

        count = {}
        failed = []
        for i in self.sequencings:
            proj = i.mgproject
            # if proj != 'PASO':
            # print(proj)
            if i.sequencing_info is not None:
                # print('Seq info here')
                if i.sequencing_info.bases > 0:
                    # print('bases!')
                    bases = i.sequencing_info.bases
                    if proj in count:
                        count[proj] = count[proj] + bases
                    else:
                        count[proj] = bases

                else:
                    # print('size_mb here')
                    bases = 0
                    for k, v in i.sequencing_info.size_mb.items():
                        bases += v

                    bases = bases*1800000
                    # bases = bases*4000000
                    if proj in count:
                        count[proj] = count[proj] + bases
                    else:
                        count[proj] = bases
            else:
                failed.append(i.mgid)

        return (count, failed)

    def find_all_assoc_sequencings(self, a):
        if 'sequencing' in a.associated:
            seqs = [Sequencing(i, db=self.db, check=False) for i in a.associated['sequencing'] if i != 'None']
            # find all samples from those reads
            all_samples = []
            for s in seqs:
                if 'sample' in s.associated:
                    samples = [Sample(i, db=self.db, check=False) for i in s.associated['sample'] if i != 'None']
                    all_samples += samples
            # Now go back - find all sequencings from all of those samples
            all_associated_seqs = []
            for s in all_samples:
                if 'sequencing' in s.associated:
                    seqs = [Sequencing(i, db=self.db, check=False) for i in s.associated['sequencing'] if i != 'None']
                    all_associated_seqs += seqs

            return all_associated_seqs
