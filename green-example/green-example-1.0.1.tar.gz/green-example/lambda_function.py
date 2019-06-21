import greengrasssdk
import json
from threading import Timer
import arrow

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# When deployed to a Greengrass core, this code will be executed immediately
# as a long-lived lambda function.  The code will enter the infinite while loop
# below.
def greengrass_hello_world_run():
  utc = arrow.utcnow()
  print(utc)
  client.publish(topic='green/example',
                  payload='Hello world! Sent from green-example with time {}.'.format(utc))
  # Asynchronously schedule this function to be run again in 5 seconds
  Timer(5, greengrass_hello_world_run).start()


# Execute the function above
greengrass_hello_world_run()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
  return
