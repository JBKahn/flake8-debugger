# coding: utf-8	

from __future__ import with_statement	
from setuptools import setup	


def get_version(fname='flake8_debugger.py'):	
    with open(fname) as f:	
        for line in f:	
            if line.startswith('__version__'):	
                return eval(line.split('=')[-1])	


def get_long_description():	
    descr = []	
    for fname in ('README.md',):	
        with open(fname) as f:	
            descr.append(f.read())	
    return '\n\n'.join(descr)	


install_requires = ['flake8>=1.5', 'pycodestyle']	

test_requires = ['pytest', 'flake8>=1.5', 'pycodestyle']	

setup(	
    name='flake8-debugger',	
    version=get_version(),	
    description="ipdb/pdb statement checker plugin for flake8",	
    long_description=get_long_description(),	
    keywords='flake8 debugger ipdb pdb',	
    author='Joseph Kahn',	
    author_email='josephbkahn@gmail.com',	
    url='https://github.com/jbkahn/flake8-debugger',	
    license='MIT',	
    py_modules=['flake8_debugger'],	
    zip_safe=False,	
    entry_points={	
        'flake8.extension': [	
            'T100 = flake8_debugger:DebuggerChecker',	
        ],	
    },	
    install_requires=install_requires,	
    tests_require=test_requires,	
    setup_requires=['pytest-runner'],	
    test_suite="nose.collector",	
    classifiers=[	
        'Development Status :: 4 - Beta',	
        'Environment :: Console',	
        'Framework :: Flake8',	
        'Intended Audience :: Developers',	
        'License :: OSI Approved :: MIT License',	
        'Operating System :: OS Independent',	
        'Programming Language :: Python',	
        'Topic :: Software Development :: Libraries :: Python Modules',	
        'Topic :: Software Development :: Quality Assurance',	
        'Programming Language :: Python :: 2.7',	
        'Programming Language :: Python :: 3.4',	
        'Programming Language :: Python :: 3.5',	
    ],	
)