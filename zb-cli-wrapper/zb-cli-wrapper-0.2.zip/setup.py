#
# Copyright (c) 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Setup script for zb_cli_wrapper.

USAGE:
    python setup.py install
    python setup.py sdist

"""
import setuptools


def setup():
    setuptools.setup(
        name='zb-cli-wrapper',
        version="0.2",
        author="Nordic Semiconductor ASA",
        description='Nordic Semiconductor zb_cli_wrapper Python library',
        url='https://www.nordicsemi.com',
        long_description='A Python package that includes the wrapper for Nordic Zigbee CLI Agent example',
        license='5-Clause Nordic License',
        classifiers=[
            'Development Status :: 3 - Alpha',

            'Intended Audience :: Developers',

            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',

            'Topic :: System :: Networking',
            'Topic :: Software Development :: Embedded Systems',

            'License :: Other/Proprietary License',

            'Programming Language :: Python :: 3.6',

            'Programming Language :: Python :: 3.7'
        ],
        keywords='nordic nrf52840 zigbee cli_wrapper',
        packages=setuptools.find_packages(include=["zb_cli_wrapper*"], exclude=['*scripts*']),
        python_requires='~=3.6',
        install_requires=[
            "pynrfjprog~=9.8.0",
            "pyserial",
            "pyyaml"
        ],
        include_package_data=True
    )


if __name__ == '__main__':
    setup()
