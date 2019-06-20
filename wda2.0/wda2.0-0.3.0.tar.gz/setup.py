from setuptools import setup, find_packages
def main():
    setup(
        name='wda2.0',
        version='0.3.0',
        description='just for test',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
        ],
        author='landy',
        url='https://github.com/rere332/wda.git',
        author_email='landy.wang@outlook.com',
        license='MIT',
        packages=['wda'],
        package_data={"wda": ["__pycache__/*.*"]},
        include_package_data=False,
        zip_safe=False,
    )


if __name__ == "__main__":
    main()