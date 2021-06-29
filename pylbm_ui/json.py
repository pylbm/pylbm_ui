# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import json
import os
import numpy as np

from .widgets.debug import debug_func

@debug_func
def save_simu_config(path, filename, dx, model, test_case, lb_scheme, extra_config=None, responses=None):
    if not os.path.exists(path):
        os.makedirs(path)

    json.dump(
        {
            'dim': lb_scheme.dim,
            'dx': dx,
            'v_model': model,
            'test_case': {
                'module': test_case.__module__,
                'class': test_case.__class__.__name__,
                'args': json.loads(test_case.json(skip_defaults=True)),
            },
            'lb_scheme': {
                'module': lb_scheme.__module__,
                'class': lb_scheme.__class__.__name__,
                'args': json.loads(lb_scheme.json(skip_defaults=True)),
            },
            'extra_config': extra_config,
            'responses': responses,
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )

@debug_func
def save_param_study(path, filename, dx, model, test_case, lb_scheme, param_widget, sampling):
    if not os.path.exists(path):
        os.makedirs(path)

    samples = {}
    design = param_widget.design.design_space().keys()
    for isample, sample in enumerate(sampling):
        samples[isample] = {str(d): s for d, s in zip(design, sample)}

    json.dump(
        {
            'dim': lb_scheme.dim,
            'dx': dx,
            'v_model': model,
            'codegen': param_widget.codegen.v_model,
            'test_case': {
                'module': test_case.__module__,
                'class': test_case.__class__.__name__,
                'args': json.loads(test_case.json(skip_defaults=True)),
            },
            'lb_scheme': {
                'module': lb_scheme.__module__,
                'class': lb_scheme.__class__.__name__,
                'args': json.loads(lb_scheme.json(skip_defaults=True)),
            },
            'design_space': param_widget.design.to_json(),
            'responses': param_widget.responses.responses_list.v_model,
            'sampling_method': param_widget.sampling_method.v_model,
            'sample_size': param_widget.sample_size.v_model,
            'sampling': samples
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )

@debug_func
def save_param_study_for_simu(path, filename, design, responses):
    if not os.path.exists(path):
        os.makedirs(path)

    json.dump(
        {
            'design_space': design,
            'responses': responses,
        },
        open(os.path.join(path, filename), 'w'),
        sort_keys=True,
        indent=4,
    )

@debug_func
def save_stats(path, filename, stats):
    if not os.path.exists(path):
        os.makedirs(path)

    json_data = {}

    file = os.path.join(path, filename)
    if os.path.exists(file):
        json_data = json.load(open(file, 'r'))

    json_data['stats'] = stats
    json.dump(
        json_data,
        open(file, 'w'),
        sort_keys=True,
        indent=4,
    )

@debug_func
def save_results(path, filename, results):
    if not os.path.exists(path):
        os.makedirs(path)

    json_data = {}

    file = os.path.join(path, filename)
    if os.path.exists(file):
        json_data = json.load(open(file, 'r'))

    json_data['results'] = [{k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in r.items()} for r in results]
    json.dump(
        json_data,
        open(file, 'w'),
        sort_keys=True,
        indent=4,
    )
            
@debug_func
def save_param_study_Minamo(path, paramStudy_filename, minamo_filename, responses_widget):
    if not os.path.exists(path):
        os.makedirs(path)

    file = os.path.join(path, paramStudy_filename)
    json_data = {}
    if os.path.exists(file):
        json_data = json.load(open(file, 'r'))
        
    # minamo_data is the dictionary to store the parametric study setup and resulting database with Minamo json structure    
    minamo_data = {} 
    # chromosome describes both the design and response spaces for the current parametric study
    minamo_data["chromosome"] = {"parameters": [], 
                                 "responses": [], 
                                 "successes": []}
    # mission is requested for minamo optimization 
    minamo_data["mission"] = {"objectives": [], 
                              "constraints": [] }
    # merit criteria is requested for minamo run 
    minamo_data["merit-criteria"] = {"criteria": [{"name": "adeb", "type": "adim-deb"}],
                                     "global-objective": "adeb" }
    # chain describes the command chain to be executed to evaluate the sample points 
    #       as well as the name and structure of the parameters and responses files
    minamo_data["chain"]= {"commands": ["python simuStandAlone.py simInfo.json -param Parameters.txt"],
                           "files": {"input": [{"tag":"param-file", "path": "Parameters.txt" }], 
                                     "output": [{"tag":"resp-file", "name": "Responses.txt" }] },
                           "rules": {"parameters": {}, "responses": {}, "successes": {}} }
    # population is the database generated after the evaluation regrouping the parameters and responses values 
    #  for each sampling point (and other informations needed by Minamo like objectives, constraints,...)
    minamo_data["population"]= {"names": {"parameters": [], "responses": [], "successes": [], 
                                          "objectives": [], "constraints": [], "merit-criteria": []},
                                "points": []}
    
    # set the design space
    def addParameter(name, Id, minV, maxV, refV):
        minamo_data["chromosome"]["parameters"].append({"name": name, 
                                                        "type": "real", 
                                                        "lower-bound": minV, "upper-bound": maxV, 
                                                        "reference": refV})
        minamo_data["chain"]["rules"]["parameters"][name] = {"file": "param-file", 
                                                                    "line": Id+1, 
                                                                    "column": 1}
        minamo_data["population"]["names"]["parameters"].append(name)
    pId = 0    
    # "reduced" means the reduced names used in the json_data["results"] (-> PCP axes) 
    pnames_Minamo2Reduced, pnames_Reduced2Minamo = {}, {} 
    for p in json_data["design_space"]:
        if p["param"] == "relaxation parameters":
            # !!! names for the responses based on relaxation parameters only shows the selected s !!! 
            # !!! impossible to know from the name if the design paramter is sigma or log !!!
            # here is a name translator for minamo to be able to request sampling in logSigma_XXYY,etc... 
            # how to recover the reduced names using the widgets (as for the reduced response names below)??? 
            pname = "s"
            if p["in_log"]: 
                pname = "logS"
            if p["sigma"]:
                pname = "sigma"
                if p["in_log"]: 
                    pname = "logSigma"
            if p["srt"]:
                for relax in p["relax"]:
                    pname = f'{pname}{relax[1:]}'
                minV, maxV = p["min"], p["max"]
                refV =  (maxV+minV)/2   
                addParameter(pname, pId, minV, maxV, refV)
                pId+=1
                pnames_Minamo2Reduced[pname] = f"({', '.join(p['relax'])})"
                pnames_Reduced2Minamo[f"({', '.join(p['relax'])})"] = pname
            else:
                for relax in p["relax"]:
                    pname = f'{pname}+relax'
                    minV, maxV = p["min"], p["max"]
                    refV =  (maxV+minV)/2   
                    addParameter(pname, pId, minV, maxV, refV)
                    pId+=1
                    pnames_Minamo2Reduced[pname] = relax
                    pnames_Reduced2Minamo[relax] = pname
        else:
            pname = p["param"]
            if p["param"] == 'la': 
                pname = 'lambda' 
            minV, maxV = p["min"], p["max"]
            refV =  (maxV+minV)/2
            addParameter(pname, pId, minV, maxV, refV)
            pId+=1 
            pnames_Minamo2Reduced[pname] = pname
            pnames_Reduced2Minamo[pname] = pname
    #minamo_data['pnames_Minamo2Reduced'] = pnames_Minamo2Reduced
    # write the reference Parameters.txt file
    file = os.path.join(path, 'Parameters.txt')
    with open(file, 'w') as paramFile:
        #for minamoName, reducedName  in pnames_Minamo2Reduced.items():
        for minamoParam in minamo_data["chromosome"]["parameters"]:
            paramFile.write(f'{minamoParam["reference"]}'+'\n')
        
    # set the responses
    def addResponses(name, Id):
        minamo_data["chromosome"]["responses"].append({"name": name, 
                                                              "type": "real",
                                                              "reference": 0})
        minamo_data["chain"]["rules"]["responses"][name] = {"file": "resp-file", 
                                                                    "line": Id+1, 
                                                                    "column": 1}
        minamo_data["population"]["names"]["responses"].append(name)
    rId = 0 
    rnames_Minamo2Reduced, rnames_Reduced2Minamo = {}, {}
    for rname_textWidget in json_data['responses']:
        if "plot" in rname_textWidget: 
            continue # avoid non scalar responses (like plots)
        rname_reduced = responses_widget.responses[rname_textWidget].__str__()
        rname = rname_reduced# change the minamo name here
        addResponses(rname, rId)
        rId+=1 
        rnames_Minamo2Reduced[rname] = rname_reduced
        rnames_Reduced2Minamo[rname_reduced] = rname
    # impose LBMStability as response always computed 
    #    !!! stability is not in the pylbmui response list  !!!
    #    !!! but it is in the results after evaluation!!!
    rname_reduced = 'stability' 
    rname = 'LBMStab'
    addResponses(rname, rId)
    rId+=1 
    rnames_Minamo2Reduced[rname] = rname_reduced
    rnames_Reduced2Minamo[rname_reduced] = rname
    #minamo_data['rnames_Minamo2Reduced'] = rnames_Minamo2Reduced
    
    # add successes
    # !!! success are defined based on responses but cannot have the same name
    # !!! hrere the success is named 'stability' and it's value is a copy of the response 'LBMStab'
    def addSuccess(name, resp):
        minamo_data["chromosome"]["successes"].append({"name": name})
        line = minamo_data["chain"]["rules"]["responses"][resp]["line"]
        minamo_data["chain"]["rules"]["successes"][name] = {"file": "resp-file", 
                                                            "line": line, 
                                                            "column": 1}
        minamo_data["population"]["names"]["successes"].append(name)  
    addSuccess("stability", "LBMStab")
    
    # add the points, if evaluated
    ##############################
    def addPoint(ptId, pVals, rVals, sVals):
        point  = {"id": f'pts-{ptId}',
                  "flag": "NOTYET",
                  "parameters": list(map(str, pVals))
                  }
        
        nResps = len(rVals)
        if nResps > 0:
           point = {"id": f'pts-{ptId}',
                    "flag": "DONE",
                    "parameters": list(map(str, pVals)), 
                    "responses":  list(map(str, rVals)), 
                    "successes":  list(map(bool, sVals)), 
                    "response-successes": [True for i in range(nResps)]}
        minamo_data["population"]["points"].append(point)       
            
    if "results" in json_data.keys():
        resultsDic = {}
        nPts = 0
        for res in json_data["results"]:
            resultsDic[res["label"]] = res["values"]
            nPts = len(res["values"])
            
        for pt_Id in range(int(json_data["sample_size"])):
            p_Vals, r_Vals, s_Vals = [], [], []
            for minamoName, reducedName  in pnames_Minamo2Reduced.items():
                p_Vals.append(resultsDic[reducedName][pt_Id])
            for minamoName, reducedName  in rnames_Minamo2Reduced.items():
                r_Vals.append(resultsDic[reducedName][pt_Id])
            s_Vals = [resultsDic["stability"][pt_Id]]       
            addPoint(pt_Id, p_Vals, r_Vals, s_Vals)
            
        minamo_data["history"]= {}
        minamo_data["history"]['pts']= { 
                "minver": "",
                "build": "",
                "host": "",
                "user": "",
                "time": "",
                "tag": "doe-generator",
                "cmd": ""
            } 
    
    # write the Minamo json file 
    file = os.path.join(path, minamo_filename)
    json.dump(
        minamo_data,
        open(file, 'w'),
        indent=4,
    )
    
    ## create the minamo config file for use of the Minamo GUI
    file = os.path.join(path, 'config.minamo')
    minamoPath = '/softs/minamo/3.2.0-rc/64/gcc/8.3.1/release/bin/minamo' ## to be set as widget
    with open(file, 'w') as cfgFile: 
        cfgFile.write('# ------------------------------------------------------------------------------------------------------'+'\n')
        cfgFile.write('# This file has been created by LBMHYPE - defines all the paths related to the current Minamo project'+'\n')
        cfgFile.write('# Creation date : ???'+'\n')
        cfgFile.write('# ------------------------------------------------------------------------------------------------------'+'\n')
        cfgFile.write('[STRUCTURE]'+'\n')
        cfgFile.write(f'minamodir = {path}'+'\n')
        cfgFile.write(f'workflowdir = {path}'+'\n')
        cfgFile.write('projectname = .'+'\n')
        cfgFile.write(''+'\n')
        cfgFile.write('[WORKFLOW_MANAGER]'+'\n')
        cfgFile.write('workflowmanager = Minamo'+'\n')
        cfgFile.write(f'workflowmanagerexe = {minamoPath} '+'\n')
    
