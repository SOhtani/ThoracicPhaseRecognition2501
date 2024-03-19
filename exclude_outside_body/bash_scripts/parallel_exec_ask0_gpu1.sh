#!/bin/bash

case_num=8
gpu_id=1
seq 0 $case_num | xargs -I num -P 5 python3 main.py $gpu_id num "ask0_gpu1_case_dirname"
