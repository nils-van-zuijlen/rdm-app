#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# model.py
# Copyright (C) 2011 Simon Newton
# The datastore model

from google.appengine.ext import blobstore
from google.appengine.ext import db

SUBDEVICE_RANGE_DICT = {
  0: 'Root device only (0x0)',
  1: 'Root or all sub-devices (0x0 - 0x200, 0xffff)',
  2: 'Root or sub devices (0x0 - 0x200)',
  3: 'Only sub-devices (0x1 - 0x200)',
}


class LastUpdateTime(db.Model):
  """Tracks the last update time for each section of the index."""
  name = db.StringProperty(required=True)
  update_time = db.DateTimeProperty()


class Manufacturer(db.Model):
  """Represents a Manufacturer."""
  esta_id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)


class ProductCategory(db.Model):
  id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)


class Responder(db.Model):
  """Represents a particular RDM product / device."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  # The Device Model ID field from DEVICE_INFO
  device_model_id = db.IntegerProperty()
  # The DEVICE_MODEL_DESCRIPTION
  model_description = db.StringProperty(required=True)
  # The product category
  product_category = db.ReferenceProperty(ProductCategory,
                                          collection_name='responder_set')
  # link to the product page
  link = db.LinkProperty();
  # url of the source image
  image_url = db.LinkProperty();
  # the blob for the image data
  image_data = blobstore.BlobReferenceProperty()
  # the url we're serving the image on
  image_serving_url = db.LinkProperty()
  # the scoring rank
  score = db.IntegerProperty()
  # the score penalty, used to demote responders
  score_penalty = db.IntegerProperty()


class ResponderTag(db.Model):
  """Tags that can be applied to responders."""
  # the tag label
  label = db.StringProperty(required=True)
  exclude_from_search = db.BooleanProperty(default=False)


class ResponderTagRelationship(db.Model):
  """The glue that maps tags to responders."""
  tag = db.ReferenceProperty(ResponderTag,
                             required=True,
                             collection_name='responder_set')
  responder = db.ReferenceProperty(Responder,
                                   required=True,
                                   collection_name='tag_set')


class SoftwareVersion(db.Model):
  """Represents a particular software version on a responder."""
  # Version id
  version_id = db.IntegerProperty(required=True)
  # Version label
  label = db.StringProperty(required=True)
  # supported params
  supported_parameters = db.ListProperty(int)
  # reference to the responder this version is associated with
  responder = db.ReferenceProperty(Responder,
                                   required=True,
                                   collection_name='software_version_set')


class ResponderPersonality(db.Model):
  """Represents a personality of a responder."""
  # TODO(simon): make description required some time once we have all the data.
  description = db.StringProperty()
  index = db.IntegerProperty(required=True)
  slot_count = db.IntegerProperty(required=True)
  # reference to the responder this version is associated with
  sw_version = db.ReferenceProperty(SoftwareVersion,
                                    required=True,
                                    collection_name='personality_set')


class ResponderSensor(db.Model):
  """Represents a Sensor on a responder."""
  description = db.StringProperty(required=True)
  index = db.IntegerProperty(required=True)
  type = db.IntegerProperty(required=True)
  supports_recording = db.BooleanProperty()
  sw_version = db.ReferenceProperty(SoftwareVersion,
                                    required=True,
                                    collection_name='sensor_set')


class Controller(db.Model):
  """Represents an RDM Controller."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  name = db.StringProperty(required=True)
  # link to the product page
  link = db.LinkProperty();
  # image url
  image_url = db.LinkProperty();
  # the blob for the image data
  image_data = blobstore.BlobReferenceProperty()
  # the url we're serving the image on
  image_serving_url = db.LinkProperty()


class ControllerTag(db.Model):
  """Tags that can be applied to controller."""
  # the tag label
  label = db.StringProperty(required=True)
  exclude_from_search = db.BooleanProperty(default=False)


class ControllerTagRelationship(db.Model):
  """The glue that maps tags to controllers."""
  tag = db.ReferenceProperty(ControllerTag,
                             required=True,
                             collection_name='controller_set')
  controller = db.ReferenceProperty(Controller,
                                    required=True,
                                    collection_name='tag_set')

# About Enums & Ranges:
# If neither enums nor ranges are specified, the valid values is the range of
#   the data type.
# If enums are specified, and ranges aren't, the valid values are the enums
# If ranges are specified, the valid values are those which fall into the range
#   (inclusive).
# If both are specified, the enum values must fall into the specified ranges.

class Command(db.Model):
  """Represents a GET or SET Command Description."""
  sub_device_range = db.IntegerProperty(
      required=True,
      choices=set(xrange(4)))
  request = db.TextProperty()
  response = db.TextProperty()


class Pid(db.Model):
  """Represents a PID."""
  manufacturer = db.ReferenceProperty(Manufacturer, required=True)
  pid_id = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True);
  link = db.LinkProperty();
  notes = db.TextProperty()
  draft = db.BooleanProperty(default=False)
  get_command = db.ReferenceProperty(Command,
                                     collection_name='pid_get_command_set')
  set_command = db.ReferenceProperty(Command,
                                     collection_name='pid_set_command_set')
