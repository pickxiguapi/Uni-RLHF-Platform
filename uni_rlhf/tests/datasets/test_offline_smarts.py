import sys
import pathlib
from uni_rlhf.datasets import offline_smarts
import argparse
import shortuuid

task = 'smarts'
for e in ['cruise']:
    parser = argparse.ArgumentParser()
    project_id = str(shortuuid.uuid())
    parser.add_argument('--project_id', type=str, default=f'{project_id}')
    parser.add_argument('--domain', type=str, default='smarts')
    parser.add_argument('--task', type=str, default=f'{task}')
    parser.add_argument('--environment_name', type=str, default=f'{e}')
    parser.add_argument('--mode', type=str, default='offline', choices=['online', 'offline'])
    parser.add_argument('--sampler_type', type=str, default='random', choices=['random', 'disagreement', 'schedule', 'customization'])
    parser.add_argument('--feedback_type', type=str, default='visual', choices=['comparative', 'attribute', 'evaluative', 'visual', 'keypoint'])
    parser.add_argument('--query_num', type=int, default=2, help='number of query.')
    parser.add_argument('--query_length', type=int, default=50, help='length of each query.')
    parser.add_argument('--fps', type=int, default=30, help='fps of videos.')
    parser.add_argument('--video_width', type=int, default=100, help='width of videos.')
    parser.add_argument('--video_height', type=int, default=100, help='height of videos.')

    parser.add_argument('--save_dir', type=str, default=f'video/', help='save dir')
    cfg = parser.parse_args()

    dataset = offline_smarts.Dataset(project_id=cfg.project_id, domain=cfg.domain, task=cfg.task, environment_name=cfg.environment_name, mode=cfg.mode,
                    sampler_type=cfg.sampler_type, feedback_type=cfg.feedback_type, query_num=cfg.query_num,
                    query_length=cfg.query_length, fps=cfg.fps, video_width=cfg.video_width, video_height=cfg.video_height,
                    save_dir=cfg.save_dir)

    video_info_list, video_url_list, query_id_list = dataset.generate_video_resources()
    print(video_info_list, video_url_list, query_id_list)