from distutils.core import setup

setup(name='smolt',
      version='0.6',
      description='Hardware profiler',
      author='Mike McGrath',
      author_email='mmcgrath@fedoraproject.org',
      url='https://hosted.fedoraproject.org/projects/smolt',
      license='GPL',
      scripts=['sendProfile', 'readProfile'],
      package_dir={'client': ''},
      packages=['client'])

