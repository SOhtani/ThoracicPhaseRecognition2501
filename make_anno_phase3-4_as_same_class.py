from pathlib import Path


def read_annotation_txt(anno_txt_p):
    with open(anno_txt_p) as fr:
        img_path_class_id_list = [s.rstrip().split(" ") for s in fr.readlines()]
    return img_path_class_id_list

def save_annotation_txt(img_path_class_id_list, save_p):
    save_str = ""
    for img_path, class_id in img_path_class_id_list:
        save_str += f"{str(img_path)} {str(class_id)}\n"

    with open(save_p, "w") as fw:
        fw.write(save_str)


if __name__ == "__main__":
    save_dir = Path("/mnt/data1/input/Thoracic/k_fold/1_frame_per_sec_phase3-4_as_same")
    for data_type in ["train", "test"]:
        for cv in range(5):
            anno_txt_p = Path(f"/mnt/data1/input/Thoracic/k_fold/1_frame_per_sec/{data_type}_cv{cv}.txt")

            fusion_target_class_ids = [2, 3]
            src_class2post_fusion_class = {
                0: 0,
                1: 1,
                2: 2,
                3: 2,
                4: 3,
                5: 4,
            }

            img_path_class_id_list = read_annotation_txt(anno_txt_p)
            img_path_post_fusion_class_id_list = []
            for img_path_class_id in img_path_class_id_list:
                img_path, class_id = img_path_class_id
                post_fusion_class_id = src_class2post_fusion_class[int(class_id)]
                img_path_post_fusion_class_id_list.append([img_path, post_fusion_class_id])
            
            save_p = save_dir / anno_txt_p.name
            save_p.parent.mkdir(parents=True, exist_ok=True)
            save_annotation_txt(img_path_post_fusion_class_id_list, save_p)
