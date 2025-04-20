# my_job.py
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
data_stream = env.from_collection([1, 2, 3, 4, 5])
data_stream.map(lambda x: x * 2).print()

env.execute("Simple Flink Job")
