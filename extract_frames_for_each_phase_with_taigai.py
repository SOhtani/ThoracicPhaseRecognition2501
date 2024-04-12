from pathlib import Path
import numpy as np
import pandas as pd
import re
from tqdm import tqdm
import cv2
from concurrent.futures import ProcessPoolExecutor
from collections import Counter


def read_excel(excel_p, sheet_index=0):
    book = pd.ExcelFile(excel_p)
    df = book.parse(book.sheet_names[sheet_index])
    return df


def get_taigai_frame_list(df, fps):
    taigai_frame_list = []
    taigai_start_index = 1
    taigai_stop_index = 2
    time_index = 5
    for i, row in df.iterrows():
        row_list = row.values.tolist()
        _taigai_start = row_list[taigai_start_index]
        _taigai_stop = row_list[taigai_stop_index]
        _taigai_start_sec = time_to_seconds(_taigai_start)
        _taigai_stop_sec = time_to_seconds(_taigai_stop)
        taigai_frame_list.append([int(_taigai_start_sec * fps), int(_taigai_stop_sec * fps)])
    return taigai_frame_list


def get_taigai_flg_for_frames(taigai_frame_list):
    not_taigai = 0
    taigai = 1
    taigai_flg_for_frames = []
    for i, (taigai_start, taigai_end) in enumerate(taigai_frame_list):
        if i == 0:
            not_taigai_frame_num = taigai_start
        else:
            not_taigai_frame_num = taigai_start - bfr_end
        taigai_flg_for_frames += [not_taigai] * not_taigai_frame_num
        taigai_flg_for_frames += [taigai] * (taigai_end - taigai_start)
        bfr_end = taigai_end
    assert len(taigai_flg_for_frames) == taigai_frame_list[-1][1]
    return taigai_flg_for_frames


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


def transform_to_frame_list(phase_list, fps):
    phase_frame_list = []
    pre_end_sec = 0
    for _phase, _end_sec in phase_list:
        sec = _end_sec - pre_end_sec
        phase_frame_list += [_phase] * int(sec * fps)
        pre_end_sec = _end_sec
    return phase_frame_list


def transform_to_start_frame(phase_list):
    phase_rows = [
        [i, phase] for i, phase in enumerate(phase_list)
        if (i == 0) or (phase_list[i-1] != phase)
    ]
    return phase_rows


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


def get_each_phase_step_frame(phase_frame_list, base_step_frame):
    bfr_sec = 0
    phase_duration = []
    phase_frame_counter = Counter(phase_frame_list)
    max_frame_num = max([frame_num for frame_num in phase_frame_counter.values()])
    each_phase_step_frame = {
        class_id: max(int((frame_num / max_frame_num) * base_step_frame), 1)
        for class_id, frame_num in phase_frame_counter.items()
    }
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
    if not video_p.exists():
        video_p = video_root / f"{excel_p.stem}.mov"
    video = cv2.VideoCapture(str(video_p))
    fps = video.get(cv2.CAP_PROP_FPS)

    df_taigai = read_excel(excel_p, sheet_index=1)
    taigai_frame_list = get_taigai_frame_list(df_taigai, fps)
    taigai_flg_for_frames = get_taigai_flg_for_frames(taigai_frame_list)

    df_taigai = read_excel(excel_p, sheet_index=0)
    phase_list = get_phase_list(
        df_taigai,
        ignore_phase_ids,
        phase_index,
        time_index,)
    phase_frame_list = transform_to_frame_list(phase_list, fps)
    if len(phase_frame_list) > len(taigai_flg_for_frames):
        taigai_flg_for_frames += [0] * (len(phase_frame_list) - len(taigai_flg_for_frames))
    elif len(taigai_flg_for_frames) > len(phase_frame_list):
        taigai_flg_for_frames = [taigai_flg_for_frames[i] for i in range(len(phase_frame_list))]
    else:
        pass

    taigai_flg_for_frames = np.array(taigai_flg_for_frames)
    phase_frame_list = np.array(phase_frame_list)
    phase_frame_list[taigai_flg_for_frames == 1] = "x"

    step_frame = 60

    each_phase_step_frame = get_each_phase_step_frame(list(phase_frame_list), step_frame)

    for frame_i, class_id in tqdm(enumerate(phase_frame_list)):
        ret, frame = video.read()
        if not ret:
            break

        if upsampling:
            step_frame = each_phase_step_frame[class_id]

        if frame_i % step_frame == 0:
            frame_p = save_dir / str(class_id) / f"frame_{frame_i:08}.png"
            frame_p.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(frame_p), frame)
        
    video.release()


def main():
    # excel_dir = Path("/mnt/cloudy_N/Thoracic/input/original")
    # video_root = Path("/mnt/cloudy_N/Thoracic/input/original")
    # save_root = Path("/mnt/cloudy_N/Thoracic/input/images/upsampling")
    excel_dir = Path("/mnt/data1/Thoracic/input/original")
    video_root = Path("/mnt/data1/Thoracic/input/original")
    save_root = Path("/mnt/data1/Thoracic/input/upsampling")
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

