from pathlib import Path


if __name__ == "__main__":
    # image_root = Path("/mnt/cloudy_N/Thoracic/input/images/trial_dataset")
    image_root = Path("/mnt/data1/input/Thoracic/images/trial_dataset")

    for phase_dir in image_root.glob("*/*"):
        phase = phase_dir.name
        new_phase = f"phase_{phase}"
        new_phase_dir = phase_dir.parent / new_phase
        phase_dir.rename(new_phase_dir)

