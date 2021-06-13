import argparse
import json
import importlib
import sympy as sp
import time
## To remove (create a catalog package)
import sys
sys.path.append('..')
#######################################

import pylbm_ui
import pylbm
import schema

parser = argparse.ArgumentParser()
parser.add_argument('config', help='config file to run the simulation', type=str)
parser.add_argument('-o', '--output', help='output directory', type=str, default='Outputs')

args = parser.parse_args()

data = json.load(open(args.config))
path = args.output

lb_mod = importlib.import_module(data['lb_scheme']['module'])
lb_scheme = getattr(lb_mod, data['lb_scheme']['class'])(**data['lb_scheme']['args'])

tc_mod = importlib.import_module(data['test_case']['module'])
test_case = getattr(tc_mod, data['test_case']['class'])(**data['test_case']['args'])

to_exclude = []
extra = {}
for k, v in data['extra_config'].items():
    if k == 'la':
        symb = sp.symbols('lambda')
    else:
        symb = sp.symbols(k)
    to_exclude.append(symb)
    extra[symb] = v

simu_cfg = pylbm_ui.simulation.get_config(test_case, lb_scheme, data['dx'], exclude=to_exclude)
sol = pylbm.Simulation(simu_cfg, initialize=False)
sol.extra_parameters = extra

responses = []

fields = test_case.equation.get_fields()

domain = pylbm.Domain(simu_cfg)
time_e = test_case.duration
ref = test_case.ref_solution(time_e, domain.x, field='mass')

responses_list = pylbm_ui.widgets.responses.build_responses_list(test_case, lb_scheme)

responses = []
for r in data['responses']:
    responses.append(responses_list[r])


output = [0]*len(responses)

for i, r in enumerate(responses):
    if isinstance(r, pylbm_ui.responses.FromConfig):
        output[i] = r(simu_cfg, extra)

actions = [r for r in responses if isinstance(r, pylbm_ui.responses.DuringSimulation)]

nite = 0
total_time = 0
t1 = time.time()
while sol.t <= test_case.duration:
    sol.one_time_step()

    t3 = time.time()
    for a in actions:
        a(test_case.duration, sol)
    t4 = time.time()
    total_time += t4 - t3

    nite += 1
t2 = time.time()

print('execution', t2 - t1, total_time)

print(nite, sol.nt, sol.dt)
for i, r in enumerate(responses):
    if isinstance(r, pylbm_ui.responses.AfterSimulation):
        output[i] = r(sol)
    elif isinstance(r, pylbm_ui.responses.DuringSimulation):
        output[i] = r.value()

print(output)