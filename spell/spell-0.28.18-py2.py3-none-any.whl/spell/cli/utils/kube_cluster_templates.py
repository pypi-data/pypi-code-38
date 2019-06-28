eks_cluster_autoscaler_yaml_template = """
---
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-autoscaler
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
rules:
- apiGroups: [""]
  resources: ["events","endpoints"]
  verbs: ["create", "patch"]
- apiGroups: [""]
  resources: ["pods/eviction"]
  verbs: ["create"]
- apiGroups: [""]
  resources: ["pods/status"]
  verbs: ["update"]
- apiGroups: [""]
  resources: ["endpoints"]
  resourceNames: ["cluster-autoscaler"]
  verbs: ["get","update"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["watch","list","get","update"]
- apiGroups: [""]
  resources: ["pods","services","replicationcontrollers","persistentvolumeclaims","persistentvolumes"]
  verbs: ["watch","list","get"]
- apiGroups: ["extensions"]
  resources: ["replicasets","daemonsets"]
  verbs: ["watch","list","get"]
- apiGroups: ["policy"]
  resources: ["poddisruptionbudgets"]
  verbs: ["watch","list"]
- apiGroups: ["apps"]
  resources: ["statefulsets", "replicasets"]
  verbs: ["watch","list","get"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["watch","list","get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["create"]
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["cluster-autoscaler-status"]
  verbs: ["delete","get","update"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-autoscaler
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-autoscaler
subjects:
  - kind: ServiceAccount
    name: cluster-autoscaler
    namespace: kube-system

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: cluster-autoscaler
subjects:
  - kind: ServiceAccount
    name: cluster-autoscaler
    namespace: kube-system

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
        - image: k8s.gcr.io/cluster-autoscaler:v1.3.6
          name: cluster-autoscaler
          resources:
            limits:
              cpu: 100m
              memory: 300Mi
            requests:
              cpu: 100m
              memory: 300Mi
          command:
            - ./cluster-autoscaler
            - --v=4
            - --stderrthreshold=info
            - --cloud-provider=aws
            - --skip-nodes-with-local-storage=false
            - --nodes={}:{}:{}
          env:
            - name: AWS_REGION
              value: us-west-2
          volumeMounts:
            - name: ssl-certs
              mountPath: /etc/ssl/certs/ca-bundle.crt
              readOnly: true
          imagePullPolicy: "Always"
      volumes:
        - name: ssl-certs
          hostPath:
            path: "/etc/ssl/certs/ca-bundle.crt"
"""

eks_cluster_aws_auth_string = """- rolearn: arn:aws:iam::002219003547:role/nodes.prod.spell
  groups:
  - system:masters
"""

cluster_statsd_sink_yaml = """apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-graphite-conf
  labels:
    service: statsd-sink
data:
  nginx-graphite-conf: |-
    server {
      listen 8180;
      root /opt/graphite/webapp/content;
      index index.html;

      location /media {
        # django admin static files
        alias /usr/local/lib/python2.7/dist-packages/django/contrib/admin/media/;
      }

      location /admin/auth/admin {
        alias /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin;
      }

      location /admin/auth/user/admin {
        alias /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin;
      }

      location / {
        # checks for static file, if not found proxy to app
        try_files \$uri @app;
      }

      location @app {
        include fastcgi_params;
        fastcgi_split_path_info ^()(.*)$;
        fastcgi_pass 127.0.0.1:8080;
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
        add_header 'Access-Control-Allow-Credentials' 'true';
      }
    }
---
apiVersion: apps/v1beta1
kind: StatefulSet
metadata:
  labels:
    service: statsd-sink
  name: statsd-sink
spec:
  serviceName: statsd-sink
  selector:
    matchLabels:
      service: statsd-sink
  replicas: 1
  template:
    metadata:
      labels:
        service: statsd-sink
    spec:
      containers:
      - image: hopsoft/graphite-statsd:v0.9.15-phusion0.9.19
        imagePullPolicy: Always
        name: statsd-sink
        ports:
        - containerPort: 8125
          name: metrics-port
          protocol: UDP
        - containerPort: 8180
          name: graphite-www
          protocol: TCP
        volumeMounts:
        - name: graphite-storage
          mountPath: /opt/graphite/storage
          subPath: storage
        - name: nginx-graphite-conf
          mountPath: /etc/nginx/sites-enabled/graphite-statsd.conf
          subPath: graphite-statsd.conf
          readOnly: true
      volumes:
        - name: nginx-graphite-conf
          configMap:
            name: nginx-graphite-conf
            items:
            - key: nginx-graphite-conf
              path: graphite-statsd.conf
  volumeClaimTemplates:
  - metadata:
      name: graphite-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  labels:
    service: statsd-sink
  name: statsd-sink
spec:
  ports:
  - name: statsd-metrics
    port: 8125
    protocol: UDP
    targetPort: 8125
  selector:
    service: statsd-sink
  type: ClusterIP
  clusterIP: None
---
apiVersion: v1
kind: Service
metadata:
  labels:
    service: statsd-sink-graphite
  name: statsd-sink-graphite
spec:
  ports:
  - port: 8180
    protocol: TCP
  selector:
    service: statsd-sink
"""

eks_cluster_ambassador_lb_yaml = """
---
apiVersion: v1
kind: Service
metadata:
  name: ambassador
  labels:
    app: ambassador
    stack: serving
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-internal: 0.0.0.0/0
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: http
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  ports:
  - name: http
    port: 80
    targetPort: 80
  selector:
    app: ambassador
    stack: serving
  type: LoadBalancer
"""

# NOTE(Benno): this is for internal TCP only. For external HTTPS, we would need an ingress controller
gke_cluster_ambassador_lb_yaml = """
---
apiVersion: v1
kind: Service
metadata:
  name: ambassador
  labels:
    app: ambassador
    stack: serving
  annotations:
    cloud.google.com/load-balancer-type: "Internal"
spec:
  ports:
  - name: http
    port: 80
    targetPort: 80
  selector:
    app: ambassador
    stack: serving
  type: LoadBalancer
"""

cluster_ambassador_yaml = """
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: ambassador-admin
    stack: serving
  name: ambassador-admin
spec:
  ports:
  - name: ambassador-admin
    port: 8877
    targetPort: 8877
  selector:
    app: ambassador
    stack: serving
  type: ClusterIP
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ambassador
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: ambassador
    stack: serving
  name: ambassador
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ambassador
      stack: serving
  template:
    metadata:
      labels:
        app: ambassador
        stack: serving
    spec:
      containers:
      - env:
        - name: AMBASSADOR_NAMESPACE
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
        - name: AMBASSADOR_SINGLE_NAMESPACE
          value: "true"
        - name: STATSD_ENABLED
          value: "true"
        image: quay.io/datawire/ambassador:0.40.1
        livenessProbe:
          httpGet:
            path: /ambassador/v0/check_alive
            port: 8877
          initialDelaySeconds: 30
          periodSeconds: 30
        name: ambassador
        readinessProbe:
          httpGet:
            path: /ambassador/v0/check_ready
            port: 8877
          initialDelaySeconds: 30
          periodSeconds: 30
        resources:
          limits:
            cpu: 1
            memory: 400Mi
          requests:
            cpu: 200m
            memory: 100Mi
      restartPolicy: Always
      serviceAccountName: ambassador
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ambassador
rules:
- apiGroups:
  - ""
  resources:
  - services
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - configmaps
  verbs:
  - create
  - update
  - patch
  - get
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - secrets
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ambassador
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ambassador
subjects:
- kind: ServiceAccount
  name: ambassador
"""

eks_cluster_secret_yaml_template = """
apiVersion: v1
kind: Secret
metadata:
  name: s3secret
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: {}
  AWS_SECRET_ACCESS_KEY: {}
"""

gke_cluster_rbac_yaml_template = """
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: spell-api-access
rules:
- apiGroups: ["", "apps", "autoscaling"]
  resources: ["*"]
  verbs: ["*"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: spell-api-access-binding
subjects:
- kind: User
  name: {}
roleRef:
  kind: ClusterRole
  name: spell-api-access
  apiGroup: rbac.authorization.k8s.io
"""


def generate_eks_cluster_autoscaler_yaml(min_nodes, max_nodes, asg_name):
    return eks_cluster_autoscaler_yaml_template.format(min_nodes, max_nodes, asg_name)


def generate_eks_cluster_secret_yaml(aws_access_key, aws_secret_key):
    return eks_cluster_secret_yaml_template.format(aws_access_key, aws_secret_key)


def generate_cluster_ambassador_yaml(api_url, cloud="eks"):
    # Currently auth is disabled for external model-serving, so api_url is ignored
    if cloud == "eks":
        return eks_cluster_ambassador_lb_yaml + cluster_ambassador_yaml
    elif cloud == "gke":
        return gke_cluster_ambassador_lb_yaml + cluster_ambassador_yaml
    raise Exception("Invalid cloud provided: {}".format(cloud))


def generate_gke_cluster_rbac_yaml(service_acct_id):
    return gke_cluster_rbac_yaml_template.format(service_acct_id)
