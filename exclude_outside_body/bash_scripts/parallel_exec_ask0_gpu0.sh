#!/bin/bash

case_num=10
gpu_id=0
seq 0 $case_num | xargs -I num -P 5 python3 main.py $gpu_id num "ask0_gpu0_case_dirname"
