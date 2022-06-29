from enum import Enum
from dataclasses import dataclass
import os
from typing import List, Optional, Union

from firebase_functions import params


class Sentinel:
  ''' Class for USE_DEFAULT. '''

  def __init__(self, description):
    self.description = description


USE_DEFAULT = Sentinel('Value used to reset an option to factory defaults')
''' Used to reset a function option to factory default. '''


class VpcEgressSettings(str, Enum):
  ''' Valid settings for VPC egress. '''
  PRIVATE_RANGES_ONLY = 'PRIVATE_RANGES_ONLY'
  ALL_TRAFFIC = 'ALL_TRAFFIC'


@dataclass(frozen=True)
class VpcOptions:
  '''Configuration for a virtual private cloud (VPC).

  Attributes:
    connector: The ID of the connector to use. For maximal portability,
        prefer just an <id> instead of
        'projects/<project>/locations/<region>/connectors/<id>'.
    egress_setting: What kinds of outgoing connections can be established.
  '''
  connector: str
  egress_settings: VpcEgressSettings


class IngressSettings(str, Enum):
  '''What kind of traffic can access this Cloud Function.'''
  ALLOW_ALL = 'ALLOW_ALL'
  ALLOW_INTERNAL_ONLY = 'ALLOW_INTERNAL_ONLY'
  ALLOW_INTERNAL_AND_GCLB = 'ALLOW_INTERNAL_AND_GCLB'


class Memory(Enum):
  '''Valid memory settings.'''
  MB_256 = 256
  MB_512 = 512
  GB_1 = 1 << 10
  GB_2 = 2 << 10
  GB_4 = 4 << 10
  GB_8 = 8 << 10


@dataclass(frozen=True)
class HttpsOptions:
  '''Options available for all function types in a codebase.

  Attributes:
      region: (str) Region to deploy functions. Defaults to us-central1.
      memory: MB to allocate to function. Defaults to Memory.MB_256
      timeout_sec: Seconds before a function fails with a timeout error.
          Defaults to 60s.
      min_instances: Count of function instances that should be reserved at all
          time. Instances will be billed while idle. Defaults to 0.
      max_instances: Maximum count of function instances that can be created.
          Defaults to 1000.
      vpc: Configuration for a virtual private cloud. Defaults to no VPC.
      ingress: Configuration for what IP addresses can invoke a function.
          Defaults to all traffic.
      service_account: The service account a function should run as. Defaults to
          the default compute service account.
  '''
  allowed_origins: str = None
  allowed_methods: str = None
  region: Optional[str] = None
  memory: Union[None, int, Sentinel] = None
  timeout_sec: Union[None, int, Sentinel] = None
  min_instances: Union[None, int, Sentinel] = None
  max_instances: Union[None, int, Sentinel] = None
  vpc: Union[None, VpcOptions, Sentinel] = None
  ingress: Union[None, IngressSettings, Sentinel] = None
  service_account: Union[None, str, Sentinel] = None
  secrets: Union[None, List[str], params.ListParam, Sentinel] = None

  def metadata(self):
    return {
        'allowed_origins': self.allowed_methods,
        'allowed_methods': self.allowed_methods,
        'region': self.region,
        'memory': self.memory,
        'timeout_sec': self.timeout_sec,
        'min_instances': self.min_instances,
        'max_instances': self.max_instances,
        'vpc': self.vpc,
        'ingress': self.ingress,
        'service_account': self.service_account
    }


@dataclass(frozen=True)
class PubSubOptions:
  '''Options available for all function types in a codebase.

  Attributes:
      region: (str) Region to deploy functions. Defaults to us-central1.
      memory: MB to allocate to function. Defaults to Memory.MB_256
      timeout_sec: Seconds before a function fails with a timeout error.
          Defaults to 60s.
      min_instances: Count of function instances that should be reserved at all
          time. Instances will be billed while idle. Defaults to 0.
      max_instances: Maximum count of function instances that can be created.
          Defaults to 1000.
      vpc: Configuration for a virtual private cloud. Defaults to no VPC.
      ingress: Configuration for what IP addresses can invoke a function.
          Defaults to all traffic.
      service_account: The service account a function should run as. Defaults to
          the default compute service account.
  '''
  topic: str
  region: Union[None, str, params.StringParam, Sentinel] = None
  memory: Union[None, int, params.IntParam, Sentinel] = None
  timeout_sec: Union[None, int, params.IntParam, Sentinel] = None
  min_instances: Union[None, int, params._IntExpression, Sentinel] = None
  max_instances: Union[None, int, params.IntParam, Sentinel] = None
  vpc: Union[None, VpcOptions, Sentinel] = None
  ingress: Union[None, IngressSettings, Sentinel] = None
  service_account: Union[None, str, params.StringParam, Sentinel] = None
  secrets: Union[None, list[str], params.ListParam, Sentinel] = None

  def metadata(self):
    project = os.environ.get('GCLOUD_PROJECT')
    return {
        'apiVersion': 1,
        'minInstances': self.min_instances,
        'trigger': {
            'eventType': 'google.pubsub.topic.publish',
            'eventFilters': {
                'resource': f'projects/{project}/topics/{self.topic}',
            }
        },
        'topic': self.topic,
        'region': self.region,
        'memory': self.memory,
        'timeout_sec': self.timeout_sec,
        'min_instances': self.min_instances,
        'max_instances': self.max_instances,
        'vpc': self.vpc,
        'ingress': self.ingress,
        'service_account': self.service_account,
    }


# TODO move to private module and store state there
_options = HttpsOptions()


def set_global_options(options: HttpsOptions) -> None:
  '''Set options for all functions in a codebase.'''
  # TODO move to private module and store state there
  _options = options