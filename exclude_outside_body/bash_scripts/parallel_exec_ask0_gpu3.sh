#!/bin/bash

case_num=15
gpu_id=3
seq 0 $case_num | xargs -I num -P 5 python3 main.py $gpu_id num "ask0_gpu3_case_dirname"
