from service.send_processor import processor, creat_msg_queue
from helper.logger_setter import set_logger
from helper import decorator


@decorator.add_bar
def worker(logger, prefix, work_queue, sleep, attack, env, getfile, postfile, temp_dir, postfile_path, bar=None):
    while True:
        """
        def processor(logger, prefix, work_queue,
                      XXfinish_queue=None, XXthread_name=None, sleep=0, 
                      attack=False, env=False, getfile=False, postfile=False,
                      temp_dir=None, postfile_path=None):
        """
        processor(logger, prefix, work_queue,
                  sleep=sleep, attack=attack, env=env, getfile=getfile, postfile=postfile,
                  temp_dir=temp_dir, postfile_path=postfile_path)
        bar()
        if work_queue.empty():
            return


def normal_run(prefix, request_list=None, repeat_num=1, sleep=0, logger=None,
               attack=False, env=False, getfile=False, postfile=False, temp_dir=None, postfile_path=None):
    if logger is None: logger = set_logger("normal_run")

    # create message queue
    work_queue, _ = creat_msg_queue(repeat_num, request_list)
    """def worker(logger, prefix, work_queue, sleep, attack, env, getfile, postfile, temp_dir, postfile_path, bar=None)"""
    worker(logger, prefix, work_queue, sleep, attack, env, getfile, postfile, temp_dir, postfile_path)


if __name__ == "__main__":
    normal_run("https://52.78.82.9:8080", repeat_num=20)
