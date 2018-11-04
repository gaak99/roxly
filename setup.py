from setuptools import setup, find_packages

setup(
    name='roxly',
    description='roxly - auto-merge Orgzly/Emacs/Dropbox file revisions',
    version='0.0.0',
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
        'Click',
        #'dropbox>=7.2.1',
        'dropbox>=9.1.0',
        'pytz',
        'tzlocal',
        'pickledb',
    ],
    entry_points='''
        [console_scripts]
        roxly=roxly.scripts.clickit:cli
    ''',
    author='Glenn barry',
    author_email='gaak99@gmail.com',
    url='https://github.com/gaak99/roxly.git',
)
