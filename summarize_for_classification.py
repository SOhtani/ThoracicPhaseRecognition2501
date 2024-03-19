from pathlib import Path
import json
import csv


def read_json(json_p):
    with open(json_p) as fr:
        return json.load(fr)


if __name__ == "__main__":
    cv_root_dir = Path("/mnt/cloudy_z/src/yishikawa/result/Thoracic/result/exclude_phase6/upsampling_exclude_taigai/swin-large-w12_16xb64_in1k-256x512")
    eval_result_filename = "evaluation_epoch_3_macro.json"
    save_csv_filename = "summarized_result_epoch_3.csv"

    header = [
        "cv",
        "accuracy_top-1",
        "accuracy_top-5",
        "precision",
        "recall",
        "f1_score",
    ]
    summarized_result = [header]

    for cv_dir in cv_root_dir.glob("*"):
        if not cv_dir.is_dir():
            continue
        cv = cv_dir.name
        eval_result_file = cv_dir / eval_result_filename
        eval_result = read_json(eval_result_file)
        summarized_result.append(
            [cv] + [eval_result[metric] for metric in header[1:]]
        )

    mean_row = ["mean"]
    for i, metric in enumerate(header[1:], start=1):
        addition_val = 0
        cv_num = len(summarized_result[1:])
        for row in summarized_result[1:]:
            addition_val += row[i]
        mean = addition_val / cv_num
        mean_row.append(mean)
    summarized_result.append(mean_row)

    save_p = cv_root_dir / save_csv_filename
    with open(save_p, "w") as fw:
        csv.writer(fw).writerows(summarized_result)
