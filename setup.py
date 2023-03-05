from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'FastAPI Debug Tool'
LONG_DESCRIPTION = 'FastAPI Debug Tool'

# Setting up
setup(
       # the name must match the folder name 'debug_tool'
        name="debug_tool", 
        version=VERSION,
        author="Ropali Munshi",
        author_email="<ropali68@email.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'fastapi'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Linux :: Manjaro",
        ]
)