import nerdvision

if __name__ == '__main__':
    nerdvision.start(name="benpython",
                     tags={
                          'python_name': 'ben'
                      },
                     api_key='5d8f1431d2f93f5b448aa371248f5d0da7e4f7707e3853cd1158951203664cc5a98c8344287d99cd2fbd7b3a5d8caf48e7818a615a58120cee466a007dd5df64',
                     # api_key='5c91a6b25a9e1eb2c6e5e03a578804bb33432cf58f2a5690daaa163dd5161642e605b89f098c0908b02d0b995b061f3a9cc40df80cafcbbb19718b69a31fd975',
                     agent_settings={
                          'log_level': 'DEBUG',
                          # 'cloud_url': 'api.bbn.nerd.vision'
                          'point.cut.debug': True
                      })
