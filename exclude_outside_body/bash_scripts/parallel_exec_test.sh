#!/bin/bash

case_num=17
gpu_id=0
seq 0 $case_num | xargs -I num -P 1 python3 test.py num "dlstation_gpu0_case_dirname"
