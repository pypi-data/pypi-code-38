
import pickle as pkl
import requests
import json
import os
import sys
import argparse


class Create():

    def __init__(self,project_name,framework,project_dir,private=False):
        self.project_dir = project_dir
        self.git_url = 'https://api.github.com/user/repos'
        self.client_token = ''
        self.project_name = project_name
        self.private = private
        self.framework = framework
        
    def set_header(self):
        try:
            with open(f'{os.environ["HOME"]}/.gtoken','r') as f:
                self.client_token = f.readline()
        except:
            print('Authenticate First!!!')
            exit()
        self.headers = {
            'Authorization':f'token {self.client_token}'
        }
    
    def set_data(self):
        self.data = {
            'name':self.project_name,
            'private':self.private,
        }
    
    def create_repo(self):
        self.set_header()
        self.res = requests.post(self.git_url,data = json.dumps(self.data),headers = self.headers)
        print('Created Response ', self.res)
    
    def set_frame_dir(self):
        self.set_data()
        framedir = self.project_dir + self.framework + '/'
        if os.path.isdir(framedir):
            os.chdir(framedir)
        else:
            os.mkdir(framedir)
            os.chdir(framedir)
        if os.path.isdir(self.project_name):
            print('Project by that name already exists !!!')
            exit()
            return
        os.mkdir(self.project_name)
        os.chdir(self.project_name)
        os.system('git init')
        os.system('touch README.md')
        os.system('git add .')
        os.system('git commit -am "Init Commit"')
    
    def push(self):
        re = self.res.json()
        r = requests.get(re['url'],headers=self.headers)
        j = r.json()
        print(j)
        repo = j['html_url']
        os.system(f'git remote add origin {repo}')
        os.system('git push origin master')
    
    def run(self):
        self.set_frame_dir()
        self.create_repo()
        self.push()
        try:
            os.system('code .')
        except:
            print("Recommended installing VSCODE as IDE")

def get_new_token(username,password):
    payload = {'scopes':['repo'],'note':'new script'}
    ans = requests.post('https://api.github.com/authorizations',data=json.dumps(payload),auth=(username,password))
    j = ans.json()
    with open(f'{os.environ["HOME"]}/.gtoken','a+') as f:
        f.write(f'{j["token"]}')

def authenticate(args):
    print("Authenticating....")
    print(f'Username {args.username}')
    get_new_token(args.username,args.password)
    print('Authenticated!!')

def run(args):
    print(f'Creating Project {args.project_name}')
    c = Create(project_name=args.project_name,project_dir=args.project_dir,framework=args.framework,private=args.private)
    c.run()


def main():
    p = argparse.ArgumentParser(description='Tool for starting up a new project.')
    authenticator = p.add_subparsers(help='Authenticator takes two arguments username and password for your Github Profile.')
    ap = authenticator.add_parser('authenticate')
    ap.add_argument('-username',help='Github Username',dest='username',type=str,required=True)
    ap.add_argument('-password',help='Github Password',dest='password',type=str,required=True)
    ap.set_defaults(func=authenticate)
    sp = authenticator.add_parser('create')
    sp.add_argument('-projectname',help="Name of Your Project",dest='project_name',type=str,required=True)
    sp.add_argument('-framework',help="Framework or Language used.(Will make project folder under the frameworks folder!)",dest='framework',type=str,required=True)
    sp.add_argument('-projectdir',help="Directory where your project will be made",dest='project_dir',type=str,required=True)
    sp.add_argument('-private',help="Keeping your github repo private or public(default is Public)",dest='private',type=bool,required=False,default=False)
    sp.set_defaults(func=run)
    args = p.parse_args()
    args.func(args)
    
if __name__ == '__main__':
    main()