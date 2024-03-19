from pathlib import Path
import collections


if __name__ == "__main__":
    # image_root = Path("/mnt/data1/input/Thoracic/images/upsampling_exclude_taigai/not_taigai")
    # image_root = Path("/mnt/data1/input/Thoracic/images/1_frame_per_sec_exclude_taigai/not_taigai")
    image_root = Path("/mnt/data1/input/Thoracic/images/upsampling_considering_taigai_exclude_taigai/not_taigai")

    labels =  [image_p.parent.name for image_p in image_root.glob("**/*.png")]
    count = collections.Counter(labels)
    print(count)
    print(len(labels))



