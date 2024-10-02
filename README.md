# aiidalab-qe-pp
Plugin to perform data analysis and plotting using the pp.x code for the  [AiiDAlab Quantum ESPRESSO application](https://github.com/aiidalab/aiidalab-qe)

## Installation
To install the `aiidalab-qe-pp` plugin, follow these steps:

```shell
git clone https://github.com/AndresOrtegaGuerrero/aiidalab-qe-pp.git
cd aiidalab-qe-pp
pip install -e .
```

## Critic2 Integration

This plugin utilizes [Critic2](https://aoterodelaroza.github.io/critic2/) software to compute Scanning Tunneling Microscopy (STM) images from Quantum ESPRESSO output data.
For more information on Critic2 and its capabilities, please visit the [official Critic2 website](https://aoterodelaroza.github.io/critic2/).

## Critic2 AiiDAlab Installation

For installing Critic2 in your AiiDAlab please ensure you have gfortran and cmake

```shell
mamba install gfortran
mamba install cmake
```

Then follow the instructions for [Critic2 Installation](https://aoterodelaroza.github.io/critic2/installation/)

Onced installed critic2

```bash
verdi code create core.code.installed --config code.yml
```
where code.yml for your localhost within AiiDAlab can be

```bash
---
label: 'critic2'
description: 'Critic 2 at localhost'
default_calc_job_plugin: 'critic2'
filepath_executable: '/home/jovyan/critic2/build/src/critic2'
computer: 'localhost'
prepend_text: |

append_text: ' '
```

## License
The `aiidalab-qe-pp` plugin package is released under the MIT license.
See the `LICENSE` file for more details.

## Contact

If you have any questions or suggestions, feel free to reach out:

- **Author**: Andres Ortega-Guerrero
- **Email**: [andres.ortega-guerrero@empa.ch](andres.ortega-guerrero@empa.ch)

## Acknowledgements
We acknowledge support from:
* the [NCCR MARVEL](http://nccr-marvel.ch/) funded by the Swiss National Science Foundation;
