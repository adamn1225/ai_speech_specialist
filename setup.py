#!/usr/bin/env python3
"""
Speech Coach - Professional Communication Trainer
Setup script for packaging and distribution
"""

from setuptools import setup, find_packages
import os

# Read version from VERSION file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return '2.0.2'

# Read long description from README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='speech-coach',
    version=get_version(),
    author='Speech Coach Development Team',
    author_email='support@speechcoach.dev',
    description='Professional Communication Trainer with Real-time Speech Analysis',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/adamn1225/ai_speech_specialist',
    project_urls={
        'Bug Reports': 'https://github.com/adamn1225/ai_speech_specialist/issues',
        'Source': 'https://github.com/adamn1225/ai_speech_specialist',
        'Documentation': 'https://github.com/adamn1225/ai_speech_specialist#readme',
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Education :: Training',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Qt',
    ],
    python_requires='>=3.8',
    install_requires=[
        'PyQt6>=6.5.0',
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'scikit-learn>=1.0.0',
        'librosa>=0.8.0',
        'soundfile>=0.10.0',
        'PyAudio>=0.2.11',
        'praat-parselmouth>=0.4.0',
        'pulsectl>=22.0.0;platform_system=="Linux"',
        'requests>=2.25.0',
        'openai>=0.27.0',
    ],
    extras_require={
        'dev': [
            'pyinstaller>=5.0.0',
            'pytest>=6.0.0',
            'black>=21.0.0',
            'isort>=5.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'speech-coach=main:main',
        ],
        'gui_scripts': [
            'speech-coach-gui=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.yml', '*.yaml'],
        'assets': ['*'],
    },
    keywords='speech analysis communication training ai voice coaching presentation skills',
    license='MIT',
    platforms=['Windows', 'Linux', 'macOS'],
)
