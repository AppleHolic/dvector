#!python
# -*- coding: utf-8 -*-
"""Preprocess audio files."""

from argparse import ArgumentParser
from os import listdir, makedirs
from os.path import basename, isdir, join as join_path, splitext

import torch
from librosa.util import find_files as find_audio_files

from modules.audiotoolkit import AudioToolkit


def prepare(root_paths, save_dir):
    """Extract audio files from directories and turn into spectrograms."""

    assert isdir(save_dir)

    n_speakers = 0

    for root_path in root_paths:

        spkr_ids = [entry for entry in listdir(root_path)
                    if isdir(join_path(root_path, entry))]
        spkr_paths = [join_path(root_path, spkr) for spkr in spkr_ids]

        for spkr_id, spkr_path in zip(spkr_ids, spkr_paths):

            uttr_paths = find_audio_files(spkr_path)
            uttr_ids = [splitext(basename(u))[0] for u in uttr_paths]

            print(f"Collecting {len(uttr_paths)} utterances from {spkr_path}")

            if len(uttr_paths) == 0:
                continue

            n_speakers += 1

            specs_path = join_path(save_dir, f"s{n_speakers:04d}({spkr_id})")

            makedirs(specs_path)

            with torch.no_grad():
                specs = [AudioToolkit.file_to_mel(u) for u in uttr_paths]

            for spec, uttr_id in zip(specs, uttr_ids):
                torch.save(spec, join_path(specs_path, uttr_id + '.pt'))


def parse_args():
    """Parse command-line arguments."""

    parser = ArgumentParser()
    parser.add_argument("root_paths", nargs='+',
                        help="root directory of directories of speakers")
    parser.add_argument("-s", "--save_dir", type=str, required=True,
                        help="path to the directory to save processed object")

    return parser.parse_args()


if __name__ == "__main__":
    prepare(**vars(parse_args()))
