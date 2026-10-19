# ThoracicPhaseRecognition2501

胸腔鏡下部分切除（cVATS）の手術工程分類における、最初期バージョンのデータ準備・学習データ整備スクリプト群。姉妹リポジトリ `ThoracicPhaseRecognition2601`（複数アプローチ版）・`ThoracicPhaseRecognition2602`（ロボット支援下解剖学的肺切除版）の前段にあたる。

## スクリプト索引

| ファイル | 役割 |
|---|---|
| `count_images.py` | フェーズ(label)ごとの画像枚数を集計・表示 |
| `cross_val_split_for_mmcls.py` | GroupKFoldでcase単位の交差検証split（mmclassification形式のannotationテキストを出力） |
| `exclude_phase6.py` | annotationテキストからphase6のサンプルを除外 |
| `extract_frames_for_each_phase.py` | 手術記録Excelのフェーズ区間情報に基づき、動画からフェーズごとに静止画フレームを抽出 |
| `extract_frames_for_each_phase_with_taigai.py` | 上記の体外(taigai)区間判定を加えた版（体外/体内を区別してフレーム抽出） |
| `extract_taigai_frames.py` | 体外(taigai)区間のフレームのみを抽出する意図のスクリプトだが、`extract_workflow()`が`print(df); return`で早期returnしており、以降のフレーム抽出・保存処理は現状未達（実質的に動作していない、要修正） |
| `make_anno_phase3-4_as_same_class.py` | annotationテキストでphase3とphase4を同一クラスに統合 |
| `reduce_train_data.py` | train split（`train_*.txt`）を読み込み、学習データ量を間引く |
| `rename_phase_dir.py` | フェーズ別ディレクトリ名を`phase_<n>`形式にリネーム |
| `summarize_for_classification.py` | mmclassificationの評価結果JSONを集計しCSV化 |

### `exclude_outside_body/`（体外シーン除外パイプライン）

| ファイル | 役割 |
|---|---|
| `main.py` | TensorFlow/Keras分類器で体外(outside body)フレームを判定・除外するメイン処理（`gpu_id` `number` `list_name`を引数に取る） |
| `test.py` | 引数(`number` `list_name`)を受け取り1秒sleepして表示するだけのダミー実装（実際の処理は行わない、動作確認用の空スクリプト） |
| `case_names.py` | GPU別に割り当てられたケースID一覧の定義。**現状`ask0_gpu0`〜`ask0_gpu3`の4リストのみが定義されており**、下記`bash_scripts`の一部（`dlbox1_gpu2/gpu3`・`dlstation_gpu0`）が参照するリスト名は未定義（該当スクリプトは現状そのままでは`AttributeError`になる） |
| `bash_scripts/parallel_exec_*.sh` | `main.py`(または`test.py`)を複数プロセス並列実行するシェルスクリプト群。`ask0_gpu0`〜`gpu3`はcase_names.pyのリストと対応して動作するが、`dlbox1_gpu2`・`dlbox1_gpu3`・`dls`（`dlstation_gpu0`）はリスト未定義のため現状動作しない |

### `scp_bash/`（院内サーバー間のデータ転送）

| ファイル | 役割 |
|---|---|
| `dlbox1.sh` / `dlbox2.sh` / `dls.sh` / `hpct.sh` | ファイル名は**実行元ホスト**（dlbox1/dlbox2/dls/hpct）を表し、各ホストに割り当てられたケースIDの画像データを、4スクリプトとも同一の転送先（`yishikawa@10.120.2.52`）へ`scp`転送する |

## スクリプト間の関係（重複ではなく発展版）

`extract_frames_for_each_phase.py` → `extract_frames_for_each_phase_with_taigai.py` は、前者に体外(taigai)区間判定ロジックを追加した発展版（コードの一部重複はあるが機能は異なるため統合はしていない）。`extract_taigai_frames.py` はそこから体外区間抽出のみを切り出した単機能版。`scp_bash/`配下の4スクリプトはテンプレートは共通だが、実行元ホスト（dlbox1/dlbox2/dls/hpct）ごとに担当ケースIDの割り当てが異なるため、こちらも重複ではなくホスト別の分担スクリプト（転送先は4スクリプトとも同一）。

## データについて

本リポジトリには患者データ・動画・画像そのものは含まれない。各スクリプト内のパス（`/mnt/data1/...`・`/mnt/cloudy_z/...`等）は院内の共有ストレージ上の実行環境に依存したものであり、外部で再利用する場合は環境に応じて書き換えが必要。ケースID（`W0001`等）は研究用の匿名化識別子。
