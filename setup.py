from distutils.core import setup

setup(name='django-simple-search',
      version='1.0',
      description='This django form class creates a search form for a model and generates a query from the submitted data.',
      long_description=open('readme.markdown').read(),
      author='Greg Brown',
      author_email='greg@gregbrown.co.nz',
      url='https://github.com/gregplaysguitar/django-simple-search',
      py_modules=['simple_search'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Framework :: Django',],
      )
