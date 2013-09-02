from setuptools import setup

setup(
    name='storm',
    version='0.1-dev',
    url='https://github.com/thiderman/storm',
    author='Lowe Thiderman, Niclas Helbro',
    author_email='lowe.thiderman@gmail.com, niclas.helbro@gmail.com',
    description=('inotify-based dzen2 runner'),
    license='MIT',
    entry_points={
        'console_scripts': [
            'storm = storm.storm:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ],
)
