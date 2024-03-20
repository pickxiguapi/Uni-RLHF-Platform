# -*- coding: UTF-8 -*-
import os
import sys
import pickle
import uuid
import shortuuid
import argparse
from tqdm import tqdm, trange
import gym
import d4rl
import d4rl_atari
import numpy as np
import imageio
import cv2
import pathlib
from pathlib import Path
import h5py

from uni_rlhf.datasets.base import BaseOfflineDataset
import uni_rlhf.datasets.dataset_utils as dataset_utils


class Dataset(BaseOfflineDataset):
    def __init__(self, project_id, domain, task, environment_name, mode, sampler_type, feedback_type,
                query_num, query_length, fps, video_width, video_height, save_dir):
        """AtariDataset

        Args:
            project_id(str): The uuid of project
            domain (str): The domain.
            task (str): The task.
            environment_name (str): The environment name.
            mode (str): The mode. Choices are 'online' and 'offline'.
            sampler_type (str): The sampler type. Choices are 'random', 'disagreement', 'schedule', and 'customization'.
            feedback_type (str): The feedback type. Choices are 'comparative', 'attribute', 'evaluative', 'visual', and 'keypoint'.
            query_num (int): The number of queries.
            query_length (int): The length of each query.
            fps (int): The frames per second of the videos.
            video_width (int): The width of the videos.
            video_height (int): The height of the videos.                   
            save_dir (str): The directory to save the videos.
        """
        super().__init__()
        self.project_id = project_id
        self.domain = domain
        self.task = task
        self.environment_name = environment_name
        self.mode = mode
        self.sampler_type = sampler_type
        self.feedback_type = feedback_type
        self.query_num = query_num
        self.query_length = query_length
        self.fps = fps
        self.width = video_width
        self.height = video_height
        self.save_dir = save_dir

        if not os.path.exists(os.path.join(self.save_dir, self.project_id)):
            os.makedirs(os.path.join(self.save_dir, self.project_id))

        # split episode
        self.trj_idx_list = []

        if self.feedback_type in ['comparative', 'attribute']:
            self.sample_num = 2
        elif self.feedback_type in ['evaluative', 'visual', 'keypoint']:
            self.sample_num = 1
        else:
            raise ValueError("The dataset does not support this feedback type.")

        self.over_sample = False  # todo

        # video info
        self.video_info = {}

        # dataset path
        base_url = str(pathlib.Path(__file__).parent) + f"/dataset_resource/{self.domain}"
        print(base_url)
        self.dataset_path = os.path.join(base_url, self.task, self.environment_name)
        
    def load_offline_dataset(self):
        assert self.task in ['walker', 'cheetah', 'humanoid']

        datasets = {}
        filenames = sorted(os.listdir(self.dataset_path))
        num_steps = 0
        for filename in filenames:
            dataset = h5py.File(os.path.join(self.dataset_path, filename), 'r')
            for key in dataset.keys():
                if key not in datasets:
                    datasets[key] = dataset[key][:]
                else:
                    datasets[key] = np.concatenate((datasets[key], dataset[key]))
            length = dataset['reward'].shape[0]
            num_steps += length
            print("Loaded {} offline timesteps so far...".format(int(num_steps)))

        self.datasets = qlearning_vd4rl_dataset(datasets)
        self.max_episode_steps = 500
        print("Finished, loaded {} timesteps. Max episode steps {}".format(int(self.datasets["rewards"].shape[0]), self.max_episode_steps))
        print("Datasets keys: ", self.datasets.keys())

    def get_episode_boundaries(self):
        trj_idx_list = []
        N = self.datasets['rewards'].shape[0]
        
        episode_step = 0
        start_idx, data_idx = 0, 0
        trj_idx_list = []
        for i in range(N - 1):
            done_bool = bool(self.datasets['terminals'][i])
            if done_bool:
                episode_step = 0
                trj_idx_list.append([start_idx, data_idx])
                start_idx = data_idx + 1
            episode_step += 1
            data_idx += 1
        
        trj_idx_list.append([start_idx, data_idx])
        #print(trj_idx_list)
        #print(len(trj_idx_list))
        return trj_idx_list
    
    def sample(self, trj_idx_list):
        '''
            sample query_num*query_length sequences
        '''
        trj_idx_list = np.array(trj_idx_list)
        trj_len_list = trj_idx_list[:, 1] - trj_idx_list[:, 0] + 1  # len(trj_len_list) = dataset episode num
        # print(trj_len_list)
        
        assert max(trj_len_list) > self.query_length
        total_sample_num = self.query_num * self.sample_num
        start_indices, end_indices = np.zeros(total_sample_num), np.zeros(total_sample_num)
        
        for query_count in range(total_sample_num):
            temp_count = 0
            while temp_count < 1:
                trj_idx = np.random.choice(np.arange(len(trj_idx_list) - 1))
                len_trj = trj_len_list[trj_idx]
                
                if len_trj > self.query_length:
                    if not self.over_sample:
                        time_idx = np.random.choice(len_trj - self.query_length + 1)
                    else:
                        time_idx = np.random.choice(len_trj + 1)
                        if time_idx > len_trj - self.query_length:
                            time_idx = len_trj - self.query_length
                    start_idx = trj_idx_list[trj_idx][0] + time_idx
                    end_idx = start_idx + self.query_length
                    
                    assert end_idx <= trj_idx_list[trj_idx][1] + 1
                    
                    if temp_count == 0:
                        start_indices[query_count] = start_idx
                        end_indices[query_count] = end_idx
                    
                    temp_count += 1
        
        print(f"Sample query indices {self.query_num} x {self.sample_num} successfully.")

        if self.sample_num == 2:
            start_indices_1 = np.array(start_indices[:self.query_num], dtype=np.int32)
            start_indices_2 = np.array(start_indices[self.query_num:], dtype=np.int32)
            end_indices_1 = np.array(end_indices[:self.query_num], dtype=np.int32)
            end_indices_2 = np.array(end_indices[self.query_num:], dtype=np.int32)
            return {"start_indices_1": start_indices_1,
                    "end_indices_1": end_indices_1,
                    "start_indices_2": start_indices_2,
                    "end_indices_2": end_indices_2,
                    "query_id": [str(uuid.uuid4().hex) for _ in range(len(start_indices_1))]}
        elif self.sample_num == 1:
            start_indices = np.array(start_indices, dtype=np.int32)  # shape: (total_sample_num, )
            end_indices = np.array(end_indices, dtype=np.int32)
            return {"start_indices": start_indices,
                    "end_indices": end_indices,
                    "query_id": [str(uuid.uuid4().hex) for _ in range(len(start_indices))]}

    def visualize_query(self, video_info):
        video_url_list = []
        for seg_idx in trange(self.query_num):
            frames = []
            frames_2 = []
            if self.feedback_type in ['comparative', 'attribute']:			
                start_1, start_2, end_1, end_2, query_id = (
                    video_info["start_indices_1"][seg_idx],
                    video_info["start_indices_2"][seg_idx],
                    video_info["end_indices_1"][seg_idx],
                    video_info["end_indices_2"][seg_idx],
                    video_info["query_id"][seg_idx],
                )
                start_indices = range(start_1, end_1)
                start_indices_2 = range(start_2, end_2)
            elif self.feedback_type in ['evaluative', 'visual', 'keypoint']:
                start, end, query_id = (
                    video_info["start_indices"][seg_idx],
                    video_info["end_indices"][seg_idx],
                    video_info["query_id"][seg_idx],
                )
                start_indices = range(start, end)
            else:
                raise ValueError("The dataset does not support this feedback type.")

            for t in trange(self.query_length, leave=False):
                obs = self.datasets["observations"][start_indices[t]]
                frame = cv2.resize(obs.transpose(1, 2, 0), dsize=(self.width, self.height), interpolation=cv2.INTER_CUBIC)
                frames.append(frame)
    
            if self.feedback_type in ['comparative', 'attribute']:	
                for t in trange(self.query_length, leave=False):
                    obs_2 = self.datasets["observations"][start_indices_2[t]]
                    frame = cv2.resize(obs_2.transpose(1, 2, 0), dsize=(self.width, self.height), interpolation=cv2.INTER_CUBIC)
                    frames_2.append(frame)
            
            if self.feedback_type in ['comparative', 'attribute']:	
                video = np.concatenate((np.array(frames), np.array(frames_2)), axis=2)
            else:
                video = np.array(frames)
            imageio.mimsave(os.path.join(self.save_dir, self.project_id, f"{self.environment_name}_{query_id}.mp4"), video, fps=self.fps)
            video_url = os.path.join(self.save_dir, self.project_id, f"{self.environment_name}_{query_id}.mp4")
            video_url_list.append(video_url)

            if self.feedback_type in ['visual', 'keypoint']:
                dataset_utils.video_to_frames(video_url, os.path.join(self.save_dir, self.project_id, f"{self.environment_name}_{query_id}_img"))
    
        return video_url_list

    def generate_video_resources(self):
        # 1: load offline dataset
        self.load_offline_dataset()
        # 2: get episode boundaries
        trj_idx_list = self.get_episode_boundaries()
        # 3: get sample indices
        indices_info = self.sample(trj_idx_list)
        query_id_list = indices_info['query_id']
        # 4: visualize query
        video_url_list = self.visualize_query(indices_info)
        # 5: get video info
        video_info_list = dataset_utils.reformat_video_info(indices_info)

        return video_info_list, video_url_list, query_id_list


def qlearning_vd4rl_dataset(dataset, max_episode_steps=500):
    """
    Returns datasets formatted for use by standard Q-learning algorithms,
    with observations, actions, next_observations, rewards, and a terminal
    flag.

    Original_dataset:
        dict_keys(['action', 'discount', 'observation', 'reward', 'step_type'])

    Returns:
        A dictionary containing keys:
            observations: An N x dim_obs array of observations.
            actions: An N x dim_action array of actions.
            next_observations: An N x dim_obs array of next observations.
            rewards: An N-dim float array of rewards.
            terminals: An N-dim boolean array of "done" or episode termination flags.
    """
    N = dataset['reward'].shape[0]
    obs_ = []
    next_obs_ = []
    action_ = []
    reward_ = []
    done_ = []
    
    episode_step = 0
    for i in range(N-1):
        obs = dataset['observation'][i].astype(np.uint8)
        new_obs = dataset['observation'][i + 1].astype(np.uint8)
        action = dataset['action'][i].astype(np.float32)
        reward = dataset['reward'][i].astype(np.float32)
        done_bool = (episode_step == max_episode_steps)
        
        obs_.append(obs)
        next_obs_.append(new_obs)
        action_.append(action)
        reward_.append(reward)
        done_.append(done_bool)
        episode_step += 1
                
        if done_bool:
            episode_step = 0
        
    return {
        'observations': np.array(obs_),
        'actions': np.array(action_),
        'next_observations': np.array(next_obs_),
        'rewards': np.array(reward_),
        'terminals': np.array(done_),
    }
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    project_id = str(shortuuid.uuid())
    parser.add_argument('--project_id', type=str, default=f'{project_id}')
    parser.add_argument('--domain', type=str, default='vd4rl')
    parser.add_argument('--task', type=str, default='walker')
    parser.add_argument('--environment_name', type=str, default='walker_walk_medium')
    parser.add_argument('--mode', type=str, default='offline', choices=['online', 'offline'])
    parser.add_argument('--sampler_type', type=str, default='random', choices=['random', 'disagreement', 'schedule', 'customization'])
    parser.add_argument('--feedback_type', type=str, default='comparative', choices=['comparative', 'attribute', 'evaluative', 'visual', 'keypoint'])
    parser.add_argument('--query_num', type=int, default=5, help='number of query.')
    parser.add_argument('--query_length', type=int, default=200, help='length of each query.')
    parser.add_argument('--fps', type=int, default=30, help='fps of videos.')
    parser.add_argument('--video_width', type=int, default=500, help='width of videos.')
    parser.add_argument('--video_height', type=int, default=500, help='height of videos.')

    parser.add_argument('--save_dir', type=str, default=f'video/', help='save dir')
    cfg = parser.parse_args()
    
    dataset = Dataset(project_id=cfg.project_id, domain=cfg.domain, task=cfg.task, environment_name=cfg.environment_name, mode=cfg.mode,
                    sampler_type=cfg.sampler_type, feedback_type=cfg.feedback_type, query_num=cfg.query_num,
                    query_length=cfg.query_length, fps=cfg.fps, video_width=cfg.video_width, video_height=cfg.video_height,
                    save_dir=cfg.save_dir)
    
    video_info_list, video_url_list, query_id_list = dataset.generate_video_resources()
    
    