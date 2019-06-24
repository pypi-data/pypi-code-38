# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tulips', 'tulips.resource']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.7,<7.0',
 'kubernetes>=9.0.0,<10.0.0',
 'passlib>=1.7,<2.0',
 'ruamel.yaml>=0.15.89,<0.16.0',
 'structlog>=18.1,<19.0']

setup_kwargs = {
    'name': 'tulips',
    'version': '1.4.4',
    'description': 'Wrapper around kubernetes-clients/python',
    'long_description': '[![Build Status](https://travis-ci.com/dz0ny/tulips.svg?branch=master)](https://travis-ci.com/dz0ny/tulips)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Type checker: mypy](https://img.shields.io/badge/type%20checker-mypy-1F5082.svg)](https://github.com/python/mypy)\n[![Packaging: poetry](https://img.shields.io/badge/packaging-poetry-C2CAFD.svg)](https://poetry.eustace.io/)\n[![Packaging: poetry](https://img.shields.io/badge/packaging-pypi-006dad.svg)](https://pypi.org/project/tulips/)\n[![codecov](https://codecov.io/gh/dz0ny/tulips/branch/master/graph/badge.svg)](https://codecov.io/gh/dz0ny/tulips)\n\n# Tulips\n\nA small wrapper around https://github.com/kubernetes-client/python which understands Kubernetes charts.\n\n## Why\n\nI needed something simple that would read Helm charts and push them to the Kubernetes cluster and\nbe extensible. So something like helm+kubectl with ability to write you own tools around them.\n\n## Supported CRDS aka Kubernetes resources\n\n- Deployment\n- Service\n- Ingress\n- Secret\n- Issuer (cert-manager)\n- PersistentVolumeClaim\n\n## Example use\n\n```python\n\nimport yaml\nfrom tulips.resources import ResourceRegistry\nfrom kubernetes import client as k8s\nfrom kubernetes import config\n\n\nclient = config.new_client_from_config(\'kube.conf\')\n\nspec = yaml.load(\'ingress.yaml\')\n\ningress_cls = ResourceRegistry.get_cls(spec[\'kind\'])\ningress = ingress_cls(config.client, namespace=\'default\', spec)\ningress.create()  # Create Ingress resource\ningress.delete()  # Delete Ingress resource\n```\n\n## Adding new resource\n\nIn order to add support for new Kubernetes resource, one needs to create class\nthat inherits from `tulips.resources.Resource` class.\n\n### Example resource\n\n```python\nimport tulips.resources.Resource\n\nclass ClusterIssuer(Resource):\n    """A `cert-manager` ClusterIssuer resource."""\n\n    version = "v1alpha1"\n    group = "certmanager.k8s.io"\n    plural = "clusterissuers"\n\n    def delete(self, body: k8s.V1DeleteOptions):\n        return k8s.CustomObjectsApi(\n            self.client\n        ).delete_namespaced_custom_object(\n            body=body,\n            namespace=self.namespace,\n            version=self.version,\n            group=self.group,\n            plural=self.plural,\n            name=self.name,\n        )\n\n    def create(self):\n        return k8s.CustomObjectsApi(\n            self.client\n        ).create_namespaced_custom_object(\n            body=self.resource,\n            namespace=self.namespace,\n            version=self.version,\n            group=self.group,\n            plural=self.plural,\n        )\n```\n\nIt will be registered into the `ResourceRegistry` and can be fetched via `ResourceRegistry.get_cls` method.\n\n## Tulip\n\nTulip is a sample client that emulates Helm but without `tiller`.\n\n```shell\n$ python tulips push --help                                    06/25/18 -  9:49\nUsage: tulips push [OPTIONS] CHART\n\n  You can pass chart variables via foo=bar, for example \'$ tulip push\n  app.yaml foo=bar\'\n\nOptions:\n  --namespace TEXT   Kubernetes namespace\n  --release TEXT     Name of the release\n  --kubeconfig PATH  Path to kubernetes config\n  --help             Show this message and exit.\n\n```\n\n### Example client\n\nLet\'s say that I want to deploy a Secret and Ingress\n\n```yaml\napiVersion: v1\nkind: Secret\nmetadata:\n  name: {{ release }}-secrets\ntype: Opaque\ndata:\n  password: {{ @pwd }}\n---\napiVersion: extensions/v1beta1\nkind: Ingress\nmetadata:\n  name: {{ release }}-web-ingress\n  labels:\n    app: woocart-{{ release }}\n  annotations:\n    nginx.ingress.kubernetes.io/limit-connections: "100"\n    kubernetes.io/ingress.class: nginx\nspec:\n  rules:\n  - host: {{ domain }}\n    http:\n      paths:\n        - path: /\n          backend:\n            serviceName: {{ release }}-web\n            servicePort: 80\n```\n\nIf one runs `tulip --release test push --kubeconf kube.conf app.yaml domain=test.tld\'\n\nSpec file is inspected and all `{{ variables }}` are replaced with real values. Also\nspecial `{{ @pwd }}` will generate strong password using `passlib` library.\n',
    'author': 'Janez Troha',
    'author_email': 'dz0ny@ubuntu.si',
    'url': 'https://github.com/dz0ny/tulips',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
