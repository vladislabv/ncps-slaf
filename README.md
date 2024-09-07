# Liquid Time Constant Neural Network enhanced with Self Learnable Activation Function

## Disclaimer
The project is using "Neural Circuit Policies" (ncps) [📖 Docs](https://ncps.readthedocs.io/en/latest/index.html) as a code base. 

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.
### CPU
```bash
poetry install -E cpu --with cpu
```
### GPU
```bash
poetry install -E cuda --with cuda
```

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

```python
from ncps.torch import CfC, LTC

input_size = 20
units = 28 # 28 neurons
rnn = CfC(input_size, units)
rnn = LTC(input_size, units)
```

The RNNs defined above consider fully-connected layers, i.e., as in LSTM, GRUs, and other RNNs.
The distinctiveness of NCPs is their structured wiring diagram. 
To combine the LTC or CfC model with a 

```python
from ncps.torch import CfC, LTC
from ncps.wirings import AutoNCP

wiring = AutoNCP(28, 4) # 28 neurons, 4 outputs
input_size = 20
rnn = CfC(input_size, wiring)
rnn = LTC(input_size, wiring)
```

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## Literature
```bib
@article{lechner2020neural,
  title={Neural circuit policies enabling auditable autonomy},
  author={Lechner, Mathias and Hasani, Ramin and Amini, Alexander and Henzinger, Thomas A and Rus, Daniela and Grosu, Radu},
  journal={Nature Machine Intelligence},
  volume={2},
  number={10},
  pages={642--652},
  year={2020},
  publisher={Nature Publishing Group}
}
```
