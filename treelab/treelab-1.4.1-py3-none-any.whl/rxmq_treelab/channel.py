from rx import Observable
from rx import operators as op
from rx.core import ConnectableObservable
from rx.subjects import ReplaySubject
from treelab.rxmq_treelab.rxmq_utils import compare_topics, find_subject_by_name
import time

"""
Rxmq channel class
"""


class Channel:
    def __init__(self):
        self.subjects = {}
        self.channel_bus: ReplaySubject = ReplaySubject()
        self.channel_stream: ConnectableObservable = self.channel_bus.pipe(op.publish(),
                                                                           op.replay(), op.ref_count())

    def subject(self, name: str) -> ReplaySubject:
        """
        subject not from wait
        :param name:
        :return:
        """
        subj = find_subject_by_name(self.subjects, name)
        if not subj:
            subj = ReplaySubject()
            subj.name = name
            self.subjects[name] = subj
            self.channel_bus.on_next(subj)
        return subj

    def subject_wait(self, name: str) -> ReplaySubject:
        """
        from wait
        :param name:
        :return:
        """
        subj = find_subject_by_name(self.subjects, name)
        start = time.time()
        while not subj:
            time.sleep(0.1)
            subj = ReplaySubject()
            # subj = find_subject_by_name(self.subjects, name)
            if time.time() - start > 10:
                raise ValueError('Not event ')
        return subj

    def observe(self, name: str) -> Observable:
        """
        Get an Observable for specific set of topics
        :param name:
        :return:
        """
        if all([c not in name for c in ['#', '*']]):
            subj = self.subject_wait(name)
            return subj

        return self.channel_stream.pipe(op.filter(lambda obs: compare_topics(obs.name, name)), op.merge_all())
