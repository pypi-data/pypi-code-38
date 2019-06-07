# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
import datetime
import uuid


class MeasurementRecord:
    """
    Used during payload logging, describes payload record.

    :param metrics: scoring request
    :type metrics: dict

    :param sources: source of metrics (for example: confusion matrix)
    :type sources: dict

    :param timestamp: measurement calculation timestamp (optional). If not provided current time is assigned.
    :type timestamp: str

    """

    def __init__(self, metrics, sources=None, timestamp=None):
        validate_type(metrics, "metrics", dict, True)
        validate_type(sources, "sources", dict, False)
        validate_type(timestamp, "timestamp", str, False)

        self.metrics = metrics
        self.sources = sources
        self.timestamp = timestamp

    def _to_json_new(self, subscription, monitor_uid):
        record = {
            "monitor_definition_id": monitor_uid,
            "binding_id": subscription.binding_uid,
            "subscription_id": subscription.uid,
            "asset_id": subscription.source_uid,
            'metrics': [self.metrics]
        }

        if self.timestamp is not None:
            record['timestamp'] = self.timestamp
        else:
            record['timestamp'] = str(datetime.datetime.utcnow().isoformat()) + 'Z'

        if self.sources is not None:
            record['sources'] = [self.sources]

        return record

    # TODO workaround to support monitors using old api
    def _to_json_old(self, subscription, monitor_uid):
        record = {
            "binding_id": subscription.binding_uid,
            "subscription_id": subscription.uid,
            "metric_type": monitor_uid,
            'asset_revision': '',
        }

        if self.timestamp is not None:
            record['timestamp'] = self.timestamp
        else:
            record['timestamp'] = str(datetime.datetime.utcnow().isoformat()) + 'Z'

        # TODO workaround to calculate quality metric if not explicitly provided
        if monitor_uid == 'quality':
            if 'quality' not in self.metrics.keys():
                if 'area_under_roc' in self.metrics.keys():
                    quality_metric = self.metrics['area_under_roc']
                elif 'accuracy' in self.metrics.keys():
                    quality_metric = self.metrics['accuracy']
                elif 'r2' in self.metrics.keys():
                    quality_metric = self.metrics['r2']
                else:
                    quality_metric = 0

                record['value'] = {'quality': quality_metric, 'metrics': [{"name": key, "value": value} for key, value in self.metrics.items()]}
            else:
                metrics_without_q = self.metrics
                del metrics_without_q['quality']
                record['value'] = {'quality': self.metrics['quality'], 'metrics': [{"name": key, "value": value} for key, value in metrics_without_q.items()]}
        else:
            record['value'] = self.metrics

        return record
