import threading
from service.send_processor import processor, creat_msg_queue
from helper.logger_setter import set_logger
from helper import decorator


@decorator.add_bar
def counter(finish_queue, initial_size, bar=None):
    while True:
        curr_size = finish_queue.qsize()
        bar(curr_size / initial_size)
        if finish_queue.qsize() == initial_size:
            bar(1)
            return


def worker(logger, prefix, work_queue, finish_queue, attack, env, thread_name, temp_dir):
    while True:
        if work_queue.empty():
            return
        else:
            """
            def processor(logger, prefix, work_queue,
                          finish_queue=None, thread_name=None, XXsleep=0, 
                          attack=False, env=False, XXgetfile=False, XXpostfile=False, 
                          temp_dir=None, XXpostfile_path=None):
            """
            processor(logger, prefix, work_queue, finish_queue=finish_queue, thread_name=thread_name,
                      attack=attack, env=env, temp_dir=temp_dir)


def threads_run(prefix, request_list=None, repeat_num=1, thread_num=5, logger=None, attack=False, env=False, temp_dir=None):
    if logger is None: logger = set_logger("threads_run")

    # create message queue
    work_queue, finish_queue = creat_msg_queue(repeat_num, request_list)
    initial_size = work_queue.qsize()

    # create threads list
    thread_list = []  # create thread_name
    for i in range(thread_num):
        thread_list.append('Thread-' + str(i))

    threads = []  # threads pool

    """def counter(finish_queue, initial_size, bar=None):"""
    thread = threading.Thread(target=counter, args=(finish_queue, initial_size))
    threads.append(thread)

    for tName in thread_list:  # create new thread
        """def worker(logger, prefix, work_queue, finish_queue, attack, env, thread_name, temp_dir)"""
        thread = threading.Thread(target=worker, args=(logger, prefix, work_queue, finish_queue, attack, env, tName, temp_dir))
        threads.append(thread)

    for t in threads:  # waiting for all threads start
        t.start()
    for t in threads:  # waiting for all threads done
        t.join()

    print('Exiting Main Thread')


if __name__ == "__main__":
    threads_run("https://52.78.82.9:8080", repeat_num=20, thread_num=5)
