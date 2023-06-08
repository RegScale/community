import setuptools

setuptools.setup(
    name='regscale-standalone',
    version='1.0.0',
    author='RegScale',
    author_email='info@regscale.com',
    description=('RegScale stand-alone installation.'),
    url='https://github.com/RegScale/community/tree/main/standalone',
    project_urls={
        'Documentation': 'https://regscale.readme.io/',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['requests','docker'],
    packages=setuptools.find_packages(),
    package_data={'regscale_standalone': ['atlas.env', 'db.env', 'docker-compose.yml']},
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'regscale-standalone = regscale_standalone.installer:main',
        ],
    }
)
