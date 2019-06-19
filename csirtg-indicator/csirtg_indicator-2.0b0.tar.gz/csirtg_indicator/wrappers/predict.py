
class PredictMixin(object):
    def predict(self):
        if self.itype not in ['url', 'fqdn', 'ipv4']:
            raise TypeError('%s is not supported' % self.itype)

        try:
            from csirtg_indicator.utils.predict import predict_ips, \
                predict_fqdns, predict_urls

            if self.itype == 'ipv4':
                p = predict_ips(self)
                return [p[0].probability]

            if self.itype == 'fqdn':
                p = predict_fqdns(self)
                return [p[0].probability]

            if self.itype == 'url':
                p = predict_urls(self)
                return [p[0].probability]

        except ImportError:
            print('')
            print('This requires the csirtg_ipsml_tf, csirtg_domainsml_tf and '
                  'csirtg_urlsml_tf frameworks')
            print('https://csirtgadgets.com/?tag=machine-learning')
            print('$ pip install csirtg_ipsml_tf csirtg_domainsml_tf '
                  'csirtg_urlsml_tf')
            print('')
            raise SystemExit
