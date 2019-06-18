import json

from django.core.management import BaseCommand

from django_ethereum_events.chainevents import AbstractEventReceiver
from django_ethereum_events.models import MonitoredEvent

food_chain_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
food_chain_abi = json.loads("""
[
    {
      "inputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "name",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "id",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogPlatformRegistered",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "name",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "id",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogPlatformRemoved",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "id",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "platform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "role",
          "type": "uint8"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogActorRegistered",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "id",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "platform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "role",
          "type": "uint8"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogActorRemoved",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "session",
          "type": "bytes32"
        },
        {
          "indexed": false,
          "name": "boxId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "metadata",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogBoxSessionStarted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "session",
          "type": "bytes32"
        },
        {
          "indexed": false,
          "name": "boxId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "metadata",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "LogBoxSessionEnded",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "sourceActorId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "sourcePlatform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "destinationActorId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "destinationPlatform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "payload",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "boxId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "session",
          "type": "bytes32"
        }
      ],
      "name": "LogDataHandoverRegistered",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "platform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "payload",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "boxId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "cropId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "actorId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "session",
          "type": "bytes32"
        }
      ],
      "name": "LogDataCropBlobAdded",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "platform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "payload",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "boxId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "transportId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "actorId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "session",
          "type": "bytes32"
        }
      ],
      "name": "LogDataTransportBlobAdded",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "name": "platform",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "payload",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "boxId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "warehouseId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "actorId",
          "type": "string"
        },
        {
          "indexed": false,
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "session",
          "type": "bytes32"
        }
      ],
      "name": "LogDataWarehouseBlobAdded",
      "type": "event"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "address"
        },
        {
          "name": "name",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "registerPlatform",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "address"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "removePlatform",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "string"
        },
        {
          "name": "platform",
          "type": "address"
        },
        {
          "name": "role",
          "type": "uint8"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "registerActor",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "string"
        },
        {
          "name": "platform",
          "type": "address"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "removeActor",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "boxId",
          "type": "string"
        },
        {
          "name": "metadata",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "startBoxSession",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "boxId",
          "type": "string"
        },
        {
          "name": "metadata",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "endBoxSession",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "sourceActorId",
          "type": "string"
        },
        {
          "name": "sourcePlatform",
          "type": "address"
        },
        {
          "name": "destinationActorId",
          "type": "string"
        },
        {
          "name": "destinationPlatform",
          "type": "address"
        },
        {
          "name": "payload",
          "type": "string"
        },
        {
          "name": "boxId",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "registerHandoverData",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "platform",
          "type": "address"
        },
        {
          "name": "payload",
          "type": "string"
        },
        {
          "name": "boxId",
          "type": "string"
        },
        {
          "name": "cropId",
          "type": "string"
        },
        {
          "name": "actorId",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "registerCropDataBlob",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "platform",
          "type": "address"
        },
        {
          "name": "payload",
          "type": "string"
        },
        {
          "name": "boxId",
          "type": "string"
        },
        {
          "name": "transportId",
          "type": "string"
        },
        {
          "name": "actorId",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "registerTransportDataBlob",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "platform",
          "type": "address"
        },
        {
          "name": "payload",
          "type": "string"
        },
        {
          "name": "boxId",
          "type": "string"
        },
        {
          "name": "warehouseId",
          "type": "string"
        },
        {
          "name": "actorId",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "registerWarehouseDataBlob",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "platformId",
          "type": "address"
        }
      ],
      "name": "getPlatform",
      "outputs": [
        {
          "name": "name",
          "type": "string"
        },
        {
          "name": "id",
          "type": "address"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "platformId",
          "type": "address"
        },
        {
          "name": "actorId",
          "type": "string"
        }
      ],
      "name": "getActor",
      "outputs": [
        {
          "name": "id",
          "type": "string"
        },
        {
          "name": "platform",
          "type": "address"
        },
        {
          "name": "role",
          "type": "uint8"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "boxId",
          "type": "string"
        }
      ],
      "name": "getBoxSession",
      "outputs": [
        {
          "name": "sessionId",
          "type": "bytes32"
        },
        {
          "name": "Id",
          "type": "string"
        },
        {
          "name": "metadata",
          "type": "string"
        },
        {
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    }
  ]
""")

# List of ethereum events to monitor the blockchain for
receiver = 'dev.management.commands.register_events.TestReceiver'

counter = 1

class TestReceiver(AbstractEventReceiver):

    def save(self, decoded_event):
        global counter
        print('{} - {}'.format(counter, decoded_event['event']))
        counter += 1


DEFAULT_EVENTS = [
    ('LogPlatformRegistered', food_chain_address, food_chain_abi, receiver),
    ('LogPlatformRemoved', food_chain_address, food_chain_abi, receiver),
    ('LogActorRegistered', food_chain_address, food_chain_abi, receiver),
    ('LogActorRemoved', food_chain_address, food_chain_abi, receiver),
    ('LogBoxSessionStarted', food_chain_address, food_chain_abi, receiver),
    ('LogBoxSessionEnded', food_chain_address, food_chain_abi, receiver),
    ('LogDataHandoverRegistered', food_chain_address, food_chain_abi, receiver),
    ('LogDataCropBlobAdded', food_chain_address, food_chain_abi, receiver),
    ('LogDataTransportBlobAdded', food_chain_address, food_chain_abi, receiver),
    ('LogDataWarehouseBlobAdded', food_chain_address, food_chain_abi, receiver),
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        monitored_events = MonitoredEvent.objects.all()
        for event in DEFAULT_EVENTS:

            if not monitored_events.filter(name=event[0], contract_address__iexact=event[1]).exists():
                self.stdout.write('Creating monitor for event {} at {}'.format(event[0], event[1]))

                MonitoredEvent.objects.register_event(*event)

        self.stdout.write(self.style.SUCCESS('Events are up to date'))