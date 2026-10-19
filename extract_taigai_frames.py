from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import cv2
from concurrent.futures import ProcessPoolExecutor


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


def get_not_taigai_step_frame(taigai_flg_for_frames, taigai_step_frame):
    not_taigai = 0
    taigai = 1
    taigai_frame_num = taigai_flg_for_frames.count(taigai)
    not_taigai_frame_num = taigai_flg_for_frames.count(not_taigai)
    print("taigai_frame_num", taigai_frame_num)
    print("not_taigai_frame_num", not_taigai_frame_num)
    not_taigai_step_frame = int(taigai_step_frame * not_taigai_frame_num / taigai_frame_num)
    return not_taigai_step_frame


def extract_workflow(excel_p, sheet_index, video_root, save_root, upsampling=False):
    save_dir = save_root / f"{excel_p.stem}"
    video_p = video_root / f"{excel_p.stem}.m2ts"
    if not video_p.exists():
        video_p = video_root / f"{excel_p.stem}.mov"

    video = cv2.VideoCapture(str(video_p))
    fps = video.get(cv2.CAP_PROP_FPS)

    df = read_excel(excel_p, sheet_index)
    print(df)
    # NOTE (2026-10-19): early return — the code below has never been exercised
    # end-to-end against real data in this state and is left disabled rather
    # than silently enabled. Before removing this `return`, verify at minimum:
    #   - get_not_taigai_step_frame() divides by taigai_frame_num /
    #     not_taigai_frame_num; a case with zero taigai (or zero non-taigai)
    #     segments will raise ZeroDivisionError.
    #   - time_to_seconds() assumes a specific Excel cell string format; an
    #     unexpected format raises ValueError with no case-level context.
    #   - main() below never calls .result() on the submitted Future objects,
    #     so an exception raised here would currently be silently swallowed
    #     by ProcessPoolExecutor (see fix in main()).
    #   - Validate against a small number of real cases (frame numbers, taigai
    #     labels, saved image counts) before trusting the output.
    return
    taigai_frame_list = get_taigai_frame_list(df, fps)
    taigai_flg_for_frames = get_taigai_flg_for_frames(taigai_frame_list)

    taigai_step_frame = int(fps)
    not_taigai_step_frame = get_not_taigai_step_frame(taigai_flg_for_frames, taigai_step_frame)

    for frame_i, taigai_flg in tqdm(enumerate(taigai_flg_for_frames), total=len(taigai_flg_for_frames)):
        ret, frame = video.read()
        if not ret:
            break

        step_frame = taigai_step_frame if taigai_flg else not_taigai_step_frame

        if frame_i % step_frame == 0:
            frame_p = save_dir / str(taigai_flg) / f"frame_{frame_i:09}.png"
            frame_p.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(frame_p), frame)

    video.release()


def main():
    excel_dir = Path("/mnt/data1/Thoracic/input/original")
    video_root = Path("/mnt/data1/Thoracic/input/original")
    save_root = Path("/mnt/data1/Thoracic/input/taigai_frames")
    upsampling = True
    sheet_index = 1

    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = {}
        for excel_p in excel_dir.glob("W0*.xlsx"):
            print(excel_p)
            future = executor.submit(
                extract_workflow,
                excel_p,
                sheet_index,
                video_root,
                save_root,
                upsampling)
            futures[future] = excel_p

        # NOTE (2026-10-19): without calling .result(), an exception raised
        # inside extract_workflow() for a given case is silently discarded by
        # ProcessPoolExecutor and the run looks like it "succeeded" with no
        # indication that case was never processed. Collect and report
        # failures explicitly instead.
        failed = []
        for future, excel_p in futures.items():
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] {excel_p.name} failed: {e!r}")
                failed.append((excel_p, e))
        if failed:
            print(f"[ERROR] {len(failed)} case(s) failed: "
                  f"{[p.name for p, _ in failed]}")


if __name__ == "__main__":
    main()

