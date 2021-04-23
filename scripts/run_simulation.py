import argparse
import json
import importlib

## To remove (create a catalog package)
import sys
sys.path.append('..')
#######################################

from pylbm_ui.simulation import simulation

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

simu = simulation()
simu.reset_fields(lb_scheme.equation.get_fields())

simu.reset_path(path)
simu.reset_sol(test_case, lb_scheme, data['dx'])
simu.save_config()

while simu.sol.t <= simu.duration:
    simu.sol.one_time_step()
