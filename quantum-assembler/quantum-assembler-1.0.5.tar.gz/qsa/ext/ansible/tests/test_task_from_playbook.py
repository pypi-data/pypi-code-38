import unittest



class TaskByNameFromPlaybookTestCase(unittest.TestCase):
    spec = """name: install ingress-nginx (ServiceAccount)
    tags:
    - ansible.quantumframework.org/task-impl:qsa.ext.k8s.tasks.KubernetesServiceAccountTask
    - app.kubernetes.io/part-of:ingress-nginx
    - deployment.quantumframework.org/env:global
    - kubernetes.io/resource-type:serviceaccount
    - meta.quantumframework.org/namespace:k8s.iam
    - meta.quantumframework.org/qualname:k8s.iam.nginx-ingress-serviceaccount
    - meta.quantumframework.org/version:1.0
   """


if __name__ == '__main__':
    unittest.main()
