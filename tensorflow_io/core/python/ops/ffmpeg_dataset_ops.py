# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""FFmpegDataset"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import uuid

import tensorflow as tf
from tensorflow_io.core.python.ops import io_dataset_ops

class _FFmpegIODatasetFunction(object):
  def __init__(self, function, resource, component, shape, dtype):
    self._function = function
    self._resource = resource
    self._component = component
    self._shape = shape
    self._dtype = dtype
  def __call__(self, start, stop):
    return self._function(
        self._resource, start=start, stop=stop,
        component=self._component, shape=self._shape, dtype=self._dtype)

class FFmpegIODataset(io_dataset_ops._IODataset): # pylint: disable=protected-access
  """FFmpegIODataset"""

  def __init__(self,
               filename,
               stream,
               internal=True):
    """FFmpegIODataset."""
    with tf.name_scope("FFmpegIODataset") as scope:
      from tensorflow_io.core.python.ops import ffmpeg_ops
      resource, _ = ffmpeg_ops.io_ffmpeg_readable_init(
          filename,
          container=scope,
          shared_name="%s/%s" % (filename, uuid.uuid4().hex))
      shape, dtype, _ = ffmpeg_ops.io_ffmpeg_readable_spec(resource, stream)
      shape = tf.TensorShape([None if e < 0 else e for e in shape.numpy()])
      dtype = tf.as_dtype(dtype.numpy())
      capacity = 1 if stream.startswith("v:") else 4096
      super(FFmpegIODataset, self).__init__(
          _FFmpegIODatasetFunction(
              ffmpeg_ops.io_ffmpeg_readable_read,
              resource, stream, shape, dtype),
          capacity=capacity,
          internal=internal)
