from setuptools import find_packages, setup

full_description = '''\
This is a Python module to validate the credentials of a Linux user using the /etc/shadow file.

Please take a look at the full documentation for how to install and use shadow_auth:    
* GitHub page: <https://github.com/ospinakamilo/linux-shadow-auth/>

How to use Linux Shadow Authentication:
```python
import shadow_auth

if shadow_auth.validate_with_password("username", "1234"):
    # What to do if the user is valid
    pass
    
if shadow_auth.validate_with_hash("username", "$1$TrOIigLp$FJg1nUqEQPt4OerLOWzr/1"):
    # What to do if the user is valid
    pass

#Get the algorithm and Salt for a User    
password_info = shadow_auth.get_password_info("username")
# password_info = {
#   "algorithm" = "1",
#   "salt" = "TrOIigLp"
# }

#Generate an MD5 hash
new_md5_hash = shadow_auth.generate_openssl_hash(
    algorithm=shadow_auth.Algorithm.MD5,
    salt="TrOIigLp",
    text="abcd12345",    
)
# new_md5_hash = "$1$TrOIigLp$FJg1nUqEQPt4OerLOWzr/1"

#Generate an SHA-256 hash
new_sha_256_hash = shadow_auth.generate_openssl_hash(
    algorithm=shadow_auth.Algorithm.MD5,
    salt="TrOIigLp",
    text="abcd12345",    
)
# new_sha_256_hash = "$5$TrOIigLp$6usEDvu0NgyuQ/IqQyvSBoP0x2RiNOz5izrMViHwXv2"

#Generate an SHA-512 hash
new_sha_512_hash = shadow_auth.generate_openssl_hash(
    algorithm=shadow_auth.Algorithm.MD5,
    salt="TrOIigLp",
    text="abcd12345",    
)
# new_sha_512_hash = "$6$TrOIigLp$IU0KwZfzVkuLLy/9vMFH1RgOmqE3LAGk0K9/15WOGStkeaN2IWYkY0jzCWHMUcSnnewnt9bOUwD2vStgko79v/"

``` 
'''


setup(
    name="shadow_auth",
    version="0.1",
    author="Camilo A. Ospina A.",
    author_email="camilo.ospinaa@gmail.com",
    description="Python module to validate the credentials of a Linux user using the /etc/shadow file",
    long_description=full_description,
    long_description_content_type='text/markdown',
    url="https://github.com/ospinakamilo/linux-shadow-auth/",
    keywords='shadow_auth linux authentication credentials shadow passwd pam',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],

    package_dir={"": "src"},

    packages=find_packages(
        where="src",
        exclude=["tests"],
    ),

    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*,  <4",
    
 )
