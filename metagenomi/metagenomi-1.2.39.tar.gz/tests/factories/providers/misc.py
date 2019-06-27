import factory
from faker.providers import BaseProvider


class S3PathProvider(BaseProvider):
    @classmethod
    def random_s3basepath(cls):
        r = cls.random_int(1, 300, positive=True)
        bpath = f's3://metagenomi/{r}'
        return(bpath)

    @classmethod
    def random_readfiles(cls):
        code = factory.Faker('word')
        fwd = f'{code}.1.fastq.gz'
        rev = f'{code}.2.fastq.gz'
        r = [fwd, rev]
        return(r)

factory.Faker.add_provider(S3PathProvider)


class SequencerProvider(BaseProvider):
    @classmethod
    def random_library_layout(cls):
        r = cls.random_int(1, 3)
        if r == 1:
            return('PAIRED')
        elif r == 2:
            return('SINGLE')
        elif r == 3:
            return('OTHER')

    @classmethod
    def random_library_selection(cls):
        r = cls.random_int(1, 2)
        if r == 1:
            return('RANDOM')
        elif r == 2:
            return('OTHER')

    @classmethod
    def random_library_source(cls):
        r = cls.random_int(1, 2)
        if r == 1:
            return('METAGENOMIC')
        elif r == 2:
            return('OTHER')

    @classmethod
    def random_library_strategy(cls):
        r = cls.random_int(1, 2)
        if r == 1:
            return('WGS')
        elif r == 2:
            return('OTHER')

    @classmethod
    def random_sequencer_model(cls):
        r = cls.random_int(1, 3)
        if r == 1:
            return('Hi-Seq4000')
        elif r == 2:
            return('Hi-Seq2500')
        elif r == 3:
            return('OTHER')

    @classmethod
    def random_sequencer_platform(cls):
        r = cls.random_int(1, 2)
        if r == 1:
            return('ILLUMINA')
        elif r == 2:
            return('OTHER')

factory.Faker.add_provider(SequencerProvider)
