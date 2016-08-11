from setuptools import setup, find_packages

setup(
  name="gaia-twitter-plugin",
  version="0.0.1",
  description="""Gaia Twitter plugin""",
  author="Matt Bertrand",
  install_requires=["gaia>=0.0.0"],
  packages=find_packages(),
  include_package_data=True,
  entry_points={
    'gaia.plugins': [
            "gaia_twitter.inputs = gaia_twitter.inputs",
            "gaia_twitter.processes = gaia_twitter.processes"
        ]
  }
)
