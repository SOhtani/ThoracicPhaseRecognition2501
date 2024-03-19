#!/bin/bash

case_num=17
gpu_id=0
seq 0 $case_num | xargs -I num -P 2 python3 main.py $gpu_id num "dlstation_gpu0_case_dirname"
