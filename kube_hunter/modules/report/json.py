import json
from kube_hunter.modules.report.base import BaseReporter


class JSONReporter(BaseReporter):
    def get_report(self, *args, **kwargs):
        report = super().get_report(*args, **kwargs)
        return json.dumps(report)
