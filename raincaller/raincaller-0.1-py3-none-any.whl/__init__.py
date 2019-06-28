from threading import Thread

# Thread only function
def count_string(distribution, job):    
    for c in "".join(job):
        if c not in distribution:
            distribution[c] = 1
        elif c in distribution:
            distribution[c] += 1


    

def allocate_jobs(job): 
    num_jobs=10 # NUMBER WILL BE AUTOMATICALLY DEFINED
    
    jobs = [job[int(i*len(job)/num_jobs):int((i+1)*len(job)/num_jobs)] for i in range(num_jobs)]
    return jobs

def get_distribution(data):
    # data:         list of string
    
    distribution = {}
    jobs = allocate_jobs(data)    
    
    threads = [Thread(name=f"Job{i}", target=count_string, args=(distribution, job)) for i, job in enumerate(jobs)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return distribution



