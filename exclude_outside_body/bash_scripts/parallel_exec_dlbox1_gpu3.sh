#!/bin/bash

case_num=5
gpu_id=3
seq 0 $case_num | xargs -I num -P 1 python3 main.py $gpu_id num "dlbox1_gpu3_case_dirname"

