from pathlib import Path
import numpy as np
from sklearn.model_selection import GroupKFold


def save_annotation_txt(classes, path_list, label_list, save_p):
    save_str = ""
    assert len(path_list) == len(label_list)
    for _path, _label in zip(path_list, label_list):
        class_index = classes.index(_label)
        save_str += f"{str(_path)} {class_index}\n"
    
    with open(save_p, "w") as fw:
        fw.write(save_str)


if __name__ == "__main__":
    image_root = Path("/mnt/data1/input/Thoracic/1_frame_per_sec")
    save_dir = Path("/mnt/data1/input/Thoracic/k_fold/1_frame_per_sec")
    save_dir.mkdir(parents=True, exist_ok=True)
    data_prefix = "/mnt/data1/input/Thoracic/1_frame_per_sec/"

    classes = ['1', '2', '3', '4', '5', 'x']

    image_paths = np.array([str(p).replace(data_prefix, "") for p in image_root.glob("**/*.png")])
    labels = np.array([Path(p).parent.name for p in image_paths])
    cases = np.array([Path(p).parts[-3] for p in image_paths])

    group_kfold = GroupKFold(n_splits=5)

    for i, (train_index, test_index) in enumerate(group_kfold.split(image_paths, labels, cases)):
        print("fold: ", i)
        print("test count: ", len(image_paths[test_index]))
        train_anno_p = save_dir / f"train_cv{i}.txt"
        test_anno_p = save_dir / f"test_cv{i}.txt"
        save_annotation_txt(
            classes=classes,
            path_list=image_paths[train_index],
            label_list=labels[train_index],
            save_p=train_anno_p
        )
        save_annotation_txt(
            classes=classes,
            path_list=image_paths[test_index],
            label_list=labels[test_index],
            save_p=test_anno_p
        )

