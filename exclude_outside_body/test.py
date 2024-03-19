import argparse
import time

import case_names


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int)
    parser.add_argument('list_name', type=str)
    args = parser.parse_args()
    time.sleep(1)
    print(args.number)
    list_names = getattr(case_names, args.list_name)
    print(list_names)




