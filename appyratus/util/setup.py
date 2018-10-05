import os
import re
from copy import deepcopy
from setuptools import setup, find_packages

PROJECT_CLASSIFIERS = {
    'python3': 'Programming Language :: Python :: 3',
    'mit-license': 'License :: OSI Approved :: MIT License',
    'os-independent': 'Operating System :: OS Independent'
}


class RealSetup(object):
    """
    Setup your program for the world

    All the things setuptools maybe didn't do for ya

    # Resource
    - Packaging https://packaging.python.org/tutorials/packaging-projects/
    - Licensing https://opensource.org/licenses/category
    - Versioning https://www.python.org/dev/peps/pep-0440/
    - Registering https://test.pypi.org/account/register/
    - Testing https://test.pypi.org/
    - Classifying https://pypi.org/classifiers/
    - Key projects https://packaging.python.org/key_projects/

    # Using PyPi
    ## Requirements
    ```sh
    python3 -m pip install --user --upgrade setuptools wheel twine
    ```

    ## Build
    ```sh
    python3 setup.py sdist bdist_wheel
    ```

    ## Test
    ```sh
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    python3 -m pip install --index-url https://test.pypi.org/simple/ example_pkg
    ```

    ## Production
    ```
    twine upload dist/*
    ```
    """

    def __init__(
        self,
        path=None,
        name=None,
        version=None,
        description=None,
        author=None,
        author_email=None,
        url=None,
        classifiers=None
    ):
        self.path = path or ''
        self.name = name or ''
        self.version = version or '0'
        self.description = description or ''
        self.author = author or ''
        self.author_email = author_email or ''
        self.url = url or ''
        if classifiers:
            self.classifiers = self.load_classifiers(classifiers)
        self.classifiers = classifiers or []
        self.long_description = self.load_description()
        self.requirements = self.load_requirements()
        self.scripts = self.load_scripts()
        self.packages = self.load_packages()

    def load_description(self):
        """
        Load readme
        """
        with open(os.path.join(self.path, 'README.md')) as f:
            readme = f.read()
        return readme

    def load_requirements(self):
        """
        Load requirements
        """
        requirements = []
        with open(os.path.join(self.path, 'requirements.txt')) as f:
            # requirements.txt is formatted for pip install, not setup tools.
            # As a result, we have to manually detect dependencies on github
            # and translate these into data setuptools knows how to handle.
            for line in f.readlines():
                if line.startswith('-e'):
                    # we're looking at a github repo dependency, so
                    # install from a github tarball.
                    match = re.search(
                        r'(https://github.+?)#egg=(.+)$', line.strip()
                    )
                    url, egg = match.groups()
                    if url.endswith('.git'):
                        url = url[:-4]
                    tarball_url = url.rstrip(
                        '/'
                    ) + '/tarball/master#egg=' + egg
                    requirements.append(egg)

                    # XXX wasn't in use, do we need this?
                    #dependency_links.append(tarball_url)
                else:
                    requirements.append(line.strip().replace('-', '_'))
        return requirements

    def load_scripts(self):
        """
        Load scripts found in the `bin`, also known as bin scripts
        """
        scripts = []
        bin_path = os.path.join(self.path, 'bin')
        for (dirpath, _, filenames) in os.walk(bin_path):
            for filename in filenames:
                if filename.endswith('.swp'):
                    continue
                scripts.append(os.path.join(bin_path, filename))
        return scripts

    def load_packages(self):
        """
        Load packages, setuptools does a fine job
        """
        return find_packages()

    def load_classifiers(self, keys: list):
        """
        Load classifiers providing a list of keys that exist in PROJECT_CLASSIFIERS
        """
        if not keys:
            return []
        classifiers = []
        for k in keys:
            classifier = PROJECT_CLASSIFIERS.get(k)
            if classifier:
                classifiers.append(classifier)
        return classifiers

    def run(self):
        """
        Run

        Get this thing set up already!!
        """
        # Requirements loaded from file are in order of appearance, however in
        # setuptools `setup` they are installed in reverse!  This can be
        # problematic when you have a specific order that you expect your
        # packages to be installed in, so we will reverse them here so that
        # setup reflects the correct order.
        requirements = deepcopy(self.requirements)
        requirements.reverse()
        setup(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            author_email=self.author_email,
            url=self.url,
            classifiers=self.classifiers,
            long_description=self.description,
            install_requires=requirements,
            scripts=self.scripts,
            packages=self.packages,
        )
