#!/bin/bash

case_num=9
gpu_id=2
seq 0 $case_num | xargs -I num -P 5 python3 main.py $gpu_id num "ask0_gpu2_case_dirname"
