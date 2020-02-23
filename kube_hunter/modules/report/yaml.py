from io import StringIO
from ruamel.yaml import YAML

from kube_hunter.modules.report.base import BaseReporter


class YAMLReporter(BaseReporter):
    def get_report(self, *args, **kwargs):
        report = super().get_report(*args, **kwargs)
        output = StringIO()
        yaml = YAML()
        yaml.dump(report, output)
        return output.getvalue()
