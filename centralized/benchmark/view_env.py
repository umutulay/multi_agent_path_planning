#!/usr/bin/env python3
import yaml
import matplotlib
# matplotlib.use("Agg")
from matplotlib.patches import Circle, Rectangle, Arrow
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import matplotlib.animation as manimation
import argparse
import math

Colors = ['orange', 'blue', 'green']


class Animation:
  def __init__(self, map):
    self.map = map

    aspect = map["map"]["dimensions"][0] / map["map"]["dimensions"][1]

    self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    self.ax = self.fig.add_subplot(111, aspect='equal')
    self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)
    # self.ax.set_frame_on(False)

    self.patches = []
    self.artists = []
    # create boundary patch
    xmin = -0.5
    ymin = -0.5
    xmax = map["map"]["dimensions"][0] - 0.5
    ymax = map["map"]["dimensions"][1] - 0.5

    # self.ax.relim()
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    # self.ax.set_xticks([])
    # self.ax.set_yticks([])
    # plt.axis('off')
    # self.ax.axis('tight')
    # self.ax.axis('off')

    self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
    for o in map["map"]["obstacles"]:
      x, y = o[0], o[1]
      self.patches.append(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='red', edgecolor='red'))

    # draw goals first
    for d, i in zip(map["agents"], range(0, len(map["agents"]))):
      self.patches.append(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black', alpha=0.5))
      self.patches.append(Rectangle((d["start"][0] - 0.25, d["start"][1] - 0.25), 0.5, 0.5, facecolor=Colors[1], edgecolor='black', alpha=0.5))

    # self.ax.set_axis_off()
    # self.fig.axes[0].set_visible(False)
    # self.fig.axes.get_yaxis().set_visible(False)

    # self.fig.tight_layout()

    self.anim = animation.FuncAnimation(self.fig, self.animate_func,
                               init_func=self.init_func,
                               frames=10,
                               interval=100,
                               blit=True)

  def show(self):
    plt.show()

  def init_func(self):
    for p in self.patches:
      self.ax.add_patch(p)
    for a in self.artists:
      self.ax.add_artist(a)
    return self.patches + self.artists

  def animate_func(self, i):
    return self.patches + self.artists


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="input file containing map")
    args = parser.parse_args()


    with open(args.map) as map_file:
        map = yaml.load(map_file, Loader=yaml.FullLoader)

    animation = Animation(map)
    animation.show()
