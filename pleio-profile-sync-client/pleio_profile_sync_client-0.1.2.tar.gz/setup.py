from setuptools import setup

setup(name='pleio_profile_sync_client',
      version='0.1.2',
      description='A Python client that can be used to automatically sync profile information from an identity store to a Pleio subsite.',
      url='https://gitlab.com/pleio/profile_sync_client',
      author='Stichting Pleio',
      author_email='support@pleio.nl',
      license='EUPL-1.2',
      packages=['pleio_profile_sync_client'],
      install_requires=[
          'click',
          'requests',
      ],
      python_requires='>=3.3',
      entry_points = {
          'console_scripts': ['pleio-profile-sync-client=pleio_profile_sync_client.cli:main'],
      },
      zip_safe=False)
