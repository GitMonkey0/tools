from request_vllm import generate
import time

a = ["你是谁"] * 1000
start = time.time()
b = batch_inference(a)
print(b[:5])
print(time.time() - start)
