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
import numpy as np
import imageio
import cv2
from pathlib import Path

from uni_rlhf.datasets.base import BaseOfflineDataset
import uni_rlhf.datasets.dataset_utils as dataset_utils


class Dataset(BaseOfflineDataset):
    def __init__(self, project_id, domain, task, environment_name, mode, sampler_type, feedback_type,
                query_num, query_length, fps, video_width, video_height, save_dir):
        """D4RLDataset

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
        
    def load_offline_dataset(self):
        assert self.task in ['minigrid']
        self.gym_env = gym.make(self.environment_name)
        if self.task == 'minigrid':
            self.datasets = qlearning_minigrid_dataset(self.gym_env)
        else:
            raise ValueError(f"{self.task} undefined")

        try:
            self.max_episode_steps = self.gym_env._max_episode_steps
        except:
            self.max_episode_steps = None
        print("Finished, loaded {} timesteps. Max episode steps {}".format(int(self.datasets["rewards"].shape[0]), self.max_episode_steps))
        print("Datasets keys: ", self.datasets.keys())

    def get_episode_boundaries(self):
        trj_idx_list = []
        N = self.datasets['rewards'].shape[0]
        
        # The newer version of the dataset adds an explicit
        # timeouts field. Keep old method for backwards compatability.
        use_timeouts = False
        if 'timeouts' in self.datasets:
            use_timeouts = True
        
        episode_step = 0
        start_idx, data_idx = 0, 0

        for i in range(N - 1):
            if 'maze' in self.environment_name:
                done_bool = sum(self.datasets['goals'][i + 1] - self.datasets['goals'][i]) > 0
            else:
                done_bool = bool(self.datasets['terminals'][i])
            if use_timeouts:
                final_timestep = self.datasets['timeouts'][i]
            else:
                final_timestep = (episode_step == self.max_episode_steps - 1)
            if final_timestep:
                # Skip this transition and don't apply terminals on the last step of an episode
                episode_step = 0
                trj_idx_list.append([start_idx, data_idx - 1])
                start_idx = data_idx
            if done_bool:
                episode_step = 0
                trj_idx_list.append([start_idx, data_idx])
                start_idx = data_idx + 1
            
            episode_step += 1
            data_idx += 1
        
        trj_idx_list.append([start_idx, data_idx])
        # print(trj_idx_list)
        return trj_idx_list

    def sample(self, trj_idx_list):
        '''
            sample query_num*query_length sequences
        '''
        trj_idx_list = np.array(trj_idx_list)
        trj_len_list = trj_idx_list[:, 1] - trj_idx_list[:, 0] + 1  # len(trj_len_list) = dataset episode num
        print(trj_len_list[:100])
        print(f"max(trj_len_list): {max(trj_len_list)}")
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
        # minigrid
        assert self.task in ["minigrid"]
        
        video_url_list = []
        for seg_idx in trange(self.query_num):
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
            
            frames = []
            self.gym_env.reset()
            for t in trange(self.query_length, leave=False):
                self.gym_env.set_state(self.datasets["poses"][start_indices[t]], self.datasets["orientations"][start_indices[t]])
                curr_frame = self.gym_env.render(mode="rgb_array")
                frames.append(np.flipud(curr_frame))

            if self.feedback_type in ['comparative', 'attribute']:	
                frames_2 = []
                self.gym_env.reset()
                for t in trange(self.query_length, leave=False):
                    self.gym_env.set_state(self.datasets["poses"][start_indices_2[t]], self.datasets["orientations"][start_indices_2[t]])
                    curr_frame = self.gym_env.render(mode="rgb_array")
                    frames_2.append(np.flipud(curr_frame))

            if self.feedback_type in ['comparative', 'attribute']:	
                video = np.concatenate((np.array(frames), np.array(frames_2)), axis=2)
            else:
                video = np.array(frames)
    
            writer = imageio.get_writer(os.path.join(self.save_dir, self.project_id, f"{self.gym_env.spec.id}_{query_id}.mp4"), fps=self.fps)
            for frame in tqdm(video, leave=False):
                writer.append_data(frame)
            writer.close()
            video_url = os.path.join(self.save_dir, self.project_id, f"{self.gym_env.spec.id}_{query_id}.mp4")
            video_url_list.append(video_url)

            if self.feedback_type in ['visual', 'keypoint']:
                dataset_utils.video_to_frames(video_url, os.path.join(self.save_dir, self.project_id, f"{self.gym_env.spec.id}_{query_id}_img"))
    
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


def qlearning_minigrid_dataset(env, dataset=None, terminate_on_end=False, **kwargs):
    """
    Returns datasets formatted for use by standard Q-learning algorithms,
    with observations, actions, next_observations, rewards, and a terminal
    flag.
    Args:
        env: An OfflineEnv object.
        dataset: An optional dataset to pass in for processing. If None,
            the dataset will default to env.get_dataset()
        terminate_on_end (bool): Set done=True on the last timestep
            in a trajectory. Default is False, and will discard the
            last timestep in each trajectory.
        **kwargs: Arguments to pass to env.get_dataset().
    Returns:
        A dictionary containing keys:
            observations: An N x dim_obs array of observations.
            actions: An N x dim_action array of actions.
            next_observations: An N x dim_obs array of next observations.
            rewards: An N-dim float array of rewards.
            terminals: An N-dim boolean array of "done" or episode termination flags.
    """
    if dataset is None:
        dataset = env.get_dataset(**kwargs)
    
    N = dataset["rewards"].shape[0]
    obs_ = []
    next_obs_ = []
    action_ = []
    reward_ = []
    done_ = []
    goal_ = []
    pos_ = []
    orientation_ = []
    done_bef_ = []

    
    # The newer version of the dataset adds an explicit
    # timeouts field. Keep old method for backwards compatability.
    use_timeouts = False
    if "timeouts" in dataset:
        use_timeouts = True
    
    episode_step = 0
    for i in range(N - 1):
        obs = dataset["observations"][i].astype(np.float32)
        new_obs = dataset["observations"][i + 1].astype(np.float32)
        action = dataset["actions"][i].astype(np.float32)
        reward = dataset["rewards"][i].astype(np.float32)
        done_bool = bool(dataset["terminals"][i]) or episode_step == env._max_episode_steps - 1
        goal = dataset["infos/goal"][i].astype(np.int32)
        pos = dataset["infos/pos"][i].astype(np.int32)
        orientation = dataset["infos/orientation"][i].astype(np.int32)
        
        if use_timeouts:
            final_timestep = dataset["timeouts"][i]
            next_final_timestep = dataset["timeouts"][i + 1]
        else:
            final_timestep = episode_step == env._max_episode_steps - 1
            next_final_timestep = episode_step == env._max_episode_steps - 2
        
        done_bef = bool(next_final_timestep)
        
        if (not terminate_on_end) and final_timestep:
            # Skip this transition and don't apply terminals on the last step of an episode
            episode_step = 0
            continue
        if done_bool or final_timestep:
            episode_step = 0
        
        obs_.append(obs)
        next_obs_.append(new_obs)
        action_.append(action)
        reward_.append(reward)
        done_.append(done_bool)
        goal_.append(goal)
        pos_.append(pos)
        orientation_.append(orientation)
        done_bef_.append(done_bef)

        episode_step += 1
    
    return {
        "observations": np.array(obs_),
        "actions": np.array(action_),
        "next_observations": np.array(next_obs_),
        "rewards": np.array(reward_),
        "terminals": np.array(done_),
        "goals": np.array(goal_),
        "poses": np.array(pos_),
        "orientations": np.array(orientation_),
        "dones_bef": np.array(done_bef_),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    project_id = str(shortuuid.uuid())
    parser.add_argument('--project_id', type=str, default=f'{project_id}')
    parser.add_argument('--domain', type=str, default='minigrid')
    parser.add_argument('--task', type=str, default='minigrid')
    parser.add_argument('--environment_name', type=str, default='minigrid-fourrooms-v0')
    parser.add_argument('--mode', type=str, default='offline', choices=['online', 'offline'])
    parser.add_argument('--sampler_type', type=str, default='random', choices=['random', 'disagreement', 'schedule', 'customization'])
    parser.add_argument('--feedback_type', type=str, default='comparative', choices=['comparative', 'attribute', 'evaluative', 'visual', 'keypoint'])
    parser.add_argument('--query_num', type=int, default=5, help='number of query.')
    parser.add_argument('--query_length', type=int, default=11, help='length of each query.')
    parser.add_argument('--fps', type=int, default=10, help='fps of videos.')
    parser.add_argument('--video_width', type=int, default=500, help='width of videos.')
    parser.add_argument('--video_height', type=int, default=500, help='height of videos.')

    parser.add_argument('--save_dir', type=str, default=f'video/', help='save dir')
    cfg = parser.parse_args()
    
    dataset = Dataset(project_id=cfg.project_id, domain=cfg.domain, task=cfg.task, environment_name=cfg.environment_name, mode=cfg.mode,
                        sampler_type=cfg.sampler_type, feedback_type=cfg.feedback_type, query_num=cfg.query_num,
                        query_length=cfg.query_length, fps=cfg.fps, video_width=cfg.video_width, video_height=cfg.video_height,
                        save_dir=cfg.save_dir)
    
    video_info_list, video_url_list, query_id_list = dataset.generate_video_resources()
    
    