from setuptools import setup

setup(
	name='pycola',    
	packages=[
          'pycola',
      ],
	version='0.1.59',                          
	description = 'python package to parse the job bulletins and generate a structured file',
  	author = 'Shivam Bansal',
  	author_email = 'shivam5992@gmail.com',
  	url = 'https://www.kaggle.com/shivamb/1-bulletin-structuring-engine-cola', 
  	keywords = ['text parsing', 'entity extraction', 'bulletin parser'],
    license='MIT',
    classifiers=[
    'Development Status :: 3 - Alpha',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3'      #Specify which pyhton versions that you want to support
  ],
)