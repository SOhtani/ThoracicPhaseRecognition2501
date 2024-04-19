from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import cv2
from concurrent.futures import ProcessPoolExecutor


def read_excel(excel_p):
    book = pd.ExcelFile(excel_p)
    df = book.parse(book.sheet_names[0])
    return df


def get_phase_list(df, ignore_phase_ids=[], phase_index=0, time_index=5):
    phase_list = []
    for i, row in df.iterrows():
        row_list = row.values.tolist()
        _phase = str(int(row_list[phase_index]))
        # _end_time = row_list[time_index]
        # _end_sec = time_to_seconds(_end_time)
        _end_sec = int(row_list[time_index])
        if _phase not in ignore_phase_ids:
            phase_list.append([_phase, _end_sec])
    return phase_list


def time_to_seconds(time_str):
    # 時間"分'秒"形式の正規表現
    time_pattern = re.compile(r'(\d+)\"(\d+)\'(\d+)')
    # 分'秒形式の正規表現
    minute_second_pattern = re.compile(r'(\d+)\'(\d+)')

    # 時間"分'秒"形式に一致するかチェック
    time_match = time_pattern.match(time_str)
    if time_match:
        hours, minutes, seconds = map(int, time_match.groups())
    else:
        # 時間"分'秒"形式に一致しない場合は分'秒形式をチェック
        minute_second_match = minute_second_pattern.match(time_str)
        if minute_second_match:
            hours = 0
            minutes, seconds = map(int, minute_second_match.groups())
        else:
            raise ValueError("Invalid time format")

    # 合計秒数に変換
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def get_class_id(fps, frame_cnt, phase_list):
    sec_now = frame_cnt / fps
    class_id = None
    bfr_sec = -1    #  it needs to include start_sec == 0
    for _class_id, sec in phase_list:
        if bfr_sec < sec_now <= sec:
            class_id = _class_id
        bfr_sec = sec
    return class_id


def get_each_phase_step_frame(phase_list, base_step_frame):
    bfr_sec = 0
    phase_duration = []
    for class_id, now_sec in phase_list:
        phase_duration.append([class_id, now_sec - bfr_sec])
        bfr_sec = now_sec
    max_duration =  max([duration for class_id, duration in phase_duration])
    each_phase_step_frame = {
        class_id: max(int(base_step_frame * duration / max_duration), 1)
        for class_id, duration in phase_duration}
    return each_phase_step_frame


def extract_workflow(
        excel_p,
        video_root,
        ignore_phase_ids,
        phase_index,
        time_index,
        save_root,
        upsampling=False
    ):
    save_dir = save_root / f"{excel_p.stem}"
    video_p = video_root / f"{excel_p.stem}.m2ts"
    video = cv2.VideoCapture(str(video_p))
    fps = video.get(cv2.CAP_PROP_FPS)

    df = read_excel(excel_p)
    phase_list = get_phase_list(
        df, 
        ignore_phase_ids,
        phase_index,
        time_index,)

    finish_frame_num = int(int(phase_list[-1][1]) * fps)
    step_frame = 60

    each_phase_step_frame = get_each_phase_step_frame(phase_list, step_frame)

    for frame_cnt in tqdm(list(range(finish_frame_num))):
        ret, frame = video.read()
        if not ret:
            break

        class_id = get_class_id(fps, frame_cnt, phase_list)
        if upsampling:
            step_frame = each_phase_step_frame[class_id]

        if frame_cnt % step_frame == 0:
            frame_p = save_dir / str(class_id) / f"frame_{frame_cnt:06}.png"
            frame_p.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(frame_p), frame)
        
    video.release()


def main():
    # excel_dir = Path("/mnt/cloudy_N/Thoracic/input/original")
    # video_root = Path("/mnt/cloudy_N/Thoracic/input/original")
    # save_root = Path("/mnt/cloudy_N/Thoracic/input/images/upsampling")
    excel_dir = Path("/mnt/data1/input/Thoracic/original/trial_dataset")
    video_root = Path("/mnt/data1/input/Thoracic/original/trial_dataset")
    save_root = Path("/mnt/data1/input/Thoracic/no_divide_taigai")
    upsampling = True
    ignore_phase_ids = ["6"]
    phase_index = 0
    time_index = 1

    with ProcessPoolExecutor(max_workers=5) as executor:
        for excel_p in excel_dir.glob("W00*.xlsx"):
            print(excel_p)
            executor.submit(
                extract_workflow,
                excel_p,
                video_root,
                ignore_phase_ids,
                phase_index,
                time_index,
                save_root,
                upsampling)


if __name__ == "__main__":
    main()

