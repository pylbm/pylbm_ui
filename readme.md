pylbm UI
========

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pylbm/pylbm_ui/HEAD?urlpath=voila%2Frender%2Fvoila.ipynb)

pylbm UI is a new way to explore lattice Boltzmann schemes easily and to better understand how it works. It's a work in progress but you can already try several test cases in 1d and 2d associated to lattice Boltzmann schemes. You can observe the linear stability of the scheme, plot the solution in real time and play with the parameters.

In a near future, we will add a lot of test cases and lattice Boltzmann schemes.

This user interface is based on [voilà](https://github.com/voila-dashboards/voila) and [ipyvuetify](https://github.com/mariobuikhuizen/ipyvuetify).

[pylbm](https://github.com/pylbm/pylbm) is used to build and analyse the schemes and run the simulations.

This video shows you different features of pylbm UI

https://user-images.githubusercontent.com/7510549/116612703-27725880-a938-11eb-8760-721a062d66ff.mp4

The simplest way to use is probably to click on the binder link that you can find above but it can be a little bit slow.

If you want to install locally, please follow the following steps

- Clone this repo

```
git clone https://github.com/pylbm/pylbm_ui.git
```

- Go into the repo

```
cd pylbm_ui
```

- Install the environment using `conda` or `mamba`

```
conda env create -f binder/environment.yml
```
or
```
mamba env create -f binder/environment.yml
```

- Activate the environment

```
conda activate pylbm_ui
```

- Run the interface

```
voila voila.ipynb
```

- Enjoy !

