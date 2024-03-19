from pathlib import Path


def read_annotation_txt(anno_txt_p):
    with open(anno_txt_p) as fr:
        img_path_label_list = [l.rstrip("\n").split(" ") for l in fr.readlines()]
    return img_path_label_list


def save_annotation_txt(img_path_class_list, save_p):
    save_str = ""
    for _path, _label in img_path_class_list:
        save_str += f"{str(_path)} {str(_label)}\n"
    
    with open(save_p, "w") as fw:
        fw.write(save_str)


if __name__ == "__main__":
    anno_root = Path("/mnt/cloudy_z/src/yishikawa/input/text/Thoracic/upsampling_exclude_taigai/not_taigai/k_fold")
    save_root = Path("/mnt/cloudy_z/src/yishikawa/input/text/Thoracic/exclude_phase6/upsampling_exclude_taigai/not_taigai/k_fold")
    exclude_class_id = 5

    for anno_txt in anno_root.glob("**/*.txt"):
        img_path_label_list = read_annotation_txt(anno_txt)
        excluded_target_class_list = [
            [img_path, class_id] for img_path, class_id in img_path_label_list
            if int(class_id) != exclude_class_id
        ]
        save_p = save_root / anno_txt.name
        save_annotation_txt(excluded_target_class_list, save_p)

