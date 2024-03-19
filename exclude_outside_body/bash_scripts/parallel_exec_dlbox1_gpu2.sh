#!/bin/bash

case_num=8
gpu_id=2
seq 0 $case_num | xargs -I num -P 1 python3 main.py $gpu_id num "dlbox1_gpu2_case_dirname"

