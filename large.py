from handler import executor
import time

domain = "http://ygeng-onpremise2.fortiweb-cloud-test.com:1001"
repeat_num = 1000
thread_num = 1000

while True:
	t = time.time()
	if t >= 1660777200:
		break

print("start!")
start = time.time()

for _ in range(1):
	executor.visit_attack_fast(domain, repeat_num=repeat_num, thread_num=thread_num)

end = time.time()
print("耗时: %s" % (end - start))
