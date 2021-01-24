import sys
import argparse
import itertools
import optuna
import pandas as pd
import time
import openpyxl




parser = argparse.ArgumentParser()

parser.add_argument('--trials',  type=int, default=1000, help='試行錯誤回数')
parser.add_argument('--timeout', type=int, default=60, help='制限時間')

parser.add_argument('--param', required=True, nargs='*')
parser.add_argument('--max'  , required=True, nargs='*', type=float, default=0)
parser.add_argument('--min'  , required=True, nargs='*', type=float, default=0)
parser.add_argument('--step' , required=True, nargs='*', type=float, default=0)

parser.add_argument('--target', required=True, nargs='*', type=float, default=0)
parser.add_argument('--analypath', required=True, nargs='*')
parser.add_argument('--layoutpath', required=True, nargs='*')

parser.add_argument('--historypath', required=True)

parser.add_argument('--excelpath', required=True)

args = parser.parse_args() 


for ch in itertools.combinations([len(args.param), len(args.max), len(args.min), len(args.step)], 2):
    if ch[0] != ch[1]:
        print("パラメータの数が合いません。")
        sys.exit()

if len(args.target) != len(args.analypath):
    print("パラメータの数が合いません。")
    sys.exit()


def test(a, x):
    return a * x**2 + x + a

def objective(trial):
    params = []
    for index, val in enumerate(args.param):
        params += [trial.suggest_discrete_uniform(val, args.min[index], args.max[index], args.step[index])]
    
    wb = openpyxl.load_workbook(args.excelpath)
    ws = wb.worksheets[0]
    for index, val in enumerate(params):
        ws.cell(row = 2, column = index + 1).value = val
    wb.save(args.excelpath)
    wb.close()
    
    result = []
    for index, val in enumerate(args.target):
        result += [abs(float(val))]

    aaa = abs(0 - test(params[0], params[1]))
    return aaa

study = optuna.create_study(storage="sqlite:///./example.db", study_name="aaa", load_if_exists=True)
study.optimize(objective, n_trials=args.trials, timeout=args.timeout, show_progress_bar=True)

print(study.best_value)
print(study.best_params)


df_trials = study.trials_dataframe()
df_trials.to_csv("./aaa.csv")
