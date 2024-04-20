from pathlib import Path


if __name__ == "__main__":
    base_dir = Path("/mnt/data1/input/Thoracic/k_fold/all")
    save_dir = Path("/mnt/data1/input/Thoracic/k_fold/half_train_data")
    save_dir.mkdir(parents=True, exist_ok=True)
    for base_train_txt_p in base_dir.glob("train_*.txt"):
        save_train_txt_p = save_dir / base_train_txt_p.name

        with open(base_train_txt_p) as fr:
            base_train_rows =  [
                s.rstrip().split(" ") for s in fr.readlines()]
        print(len(base_train_rows), base_train_rows[:3])

        case_ids = []
        for row in base_train_rows:
            file_path, class_id = row
            case_id = file_path.split("/")[0]
            case_ids.append(case_id)
        case_ids = list(set(case_ids))
        print(len(case_ids), sorted(case_ids)[:int(len(case_ids)/2)])

        half_case_ids = sorted(case_ids)[:int(len(case_ids)/2)]
        half_train_rows = []
        for row in base_train_rows:
            file_path, class_id = row
            case_id = file_path.split("/")[0]
            if case_id not in half_case_ids:
                continue
            half_train_rows.append(' '.join(row))
        print(len(half_train_rows), half_train_rows[:3])

        with open(save_train_txt_p, mode='w') as fw:
            fw.write('\n'.join(half_train_rows))
