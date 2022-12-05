from random import randint
from random import choice
from pprint import pprint
import logging

import cv2  # pytype:disable=import-error
from PIL import Image, ImageDraw
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_extraction import DictVectorizer
from tutorenvs.utils import OnlineDictVectorizer
import numpy as np

from tutorenvs.utils import DataShopLogger
from tutorenvs.utils import StubLogger

# begin Lane imports
from multiprocessing import Pipe
from select import select
from threading import Thread, Lock

# EXAMPLE STATE FOR OVERCOOKED:
'''
{
    'terrain': [
        ['X', 'X', 'P', 'X', 'X'],
        ['O', ' ', ' ', ' ', 'O'],
        ['X', ' ', ' ', ' ', 'X'],
        ['X', 'D', 'X', 'S', 'X']],

    'state':
        {
            'potential': None,
            'state':
                {
                    'players': [
                        {
                            'position': (1, 2),
                            'orientation': (0, -1),
                            'held_object': None
                        },
                        {
                            'position': (2, 2),
                            'orientation': (0, 1),
                            'held_object': None
                        }
                    ],
                    'objects': [],
                    'bonus_orders': [],
                    'all_orders': [{'ingredients': ('onion', 'onion', 'onion')}],
                    'timestep': 49
                },
            'score': 0,
            'time_left': 28.262798070907593
        }
}
'''

class OvercookedTutorEnv:
    def __init__(self, logger=None):
        self.state = {}
        self.state_lock = Lock()
        if logger is None:
            self.logger = DataShopLogger('OvercookedTutor', extra_kcs=['field'])
            # self.logger = StubLogger()
        else:
            self.logger = logger
        self.logger.set_student()

        # Establish async queues for publishing
        # SAIs and receiving game state
        self.sai_queue_r, self.sai_queue_w = Pipe(duplex=False)
        self.state_queue_r, self.state_queue_w = Pipe(duplex=False)

    def render(self):
        pass

    # Send the SAI out for processing in the
    # game environment. This does not block the
    # HTN loop thread.
    def publish_sai(self, s, a, i):
        print('sending action %s' % a)
        self.sai_queue_w.send((s, a, i))

    # Wait for a new state on the in-queue and
    # update it. This runs in its own thread.
    def update_state(self):
        state_channels, _, _ = select([self.state_queue_r], [], [])
        self.state_lock.acquire()
        try:
            # self.state = state_channels[0].recv()
            state_channels[0].recv()
            self.state = {}
        except:
            print('error updating state')
            pass
        self.state_lock.release()

    def get_state(self):
        # Do I actually need these locks?
        # Is copying a Python object atomic?
        # Is this even a copy...?
        self.state_lock.acquire()
        state = self.state
        self.state_lock.release()
        return state

    def apply_sai(self, s, a, i):
        # Block and wait for a state update
        self.update_state()

        # Send the SAI and fake a reward
        self.publish_sai(s, a, i)
        reward = 1.0
        return reward

    def reset(self):
        pass
