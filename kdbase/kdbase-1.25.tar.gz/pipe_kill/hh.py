from kd_pipe import *

if __name__ == '__main__':
    version = 'v4.9.0.5'
    taskid = '1561349129291'
    trackid = 
    auto_cpu_num = 
    project_id = '000000020'
    task_cmd = "env -i bash -c 'export CUDA_VISIBLE_DEVICES=99 && " \
            "/opt/mr_binary/test_lane_client_%s %s %s %s %s'" % (version, 
                    taskid, trackid, auto_cpu_num, project_id)  
    logger().info("task_cmd : %s ", task_cmd)
    task_excute_time = int(GET_CONF("auto", "task_excute_time"))
    task_max_mem = int(GET_CONF("auto", "task_max_mem"))
    logger().info('auto task task_excute_time [%d] task_max_mem [%d]',
                task_excute_time, task_max_mem)
    task_process = AdvPipe(task_cmd, task_excute_time, task_max_mem) 
    task_process.start()
    task_process.run(True)
    task_res = task_process.get_return_code()
    #task_res = tools.kdbase_system(task_cmd, task_excute_time, task_max_mem)

