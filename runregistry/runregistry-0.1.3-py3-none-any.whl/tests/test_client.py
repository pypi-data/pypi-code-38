from runregistry.runregistry import get_run, get_runs, get_dataset_names_of_run, get_dataset, get_datasets, get_lumisections, get_oms_lumisections, get_lumisection_ranges, get_oms_lumisection_ranges, get_joint_lumisection_ranges
import pytest


def test_get_run():
    run_number = 328762
    run = get_run(run_number=run_number)
    # print(run)
    assert run['run_number'] == run_number
    # Non existent run:
    run_number = 8888888888
    run = get_run(run_number=run_number)
    assert run == None


def test_get_runs():
    # Gets runs between run number 309000 and 310000
    filter_run = {
        'run_number': {
            'and': [
                {'>': 309000},
                {'<': 310000}
            ]
        },
    }
    runs = get_runs(filter=filter_run)
    assert len(runs) > 0
    # Gets runs that contain lumisections that classified DT as GOOD AND lumsiections that classified hcal as STANDBY
    filter_run = {
        'run_number': {
            'and': [
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'dt': 'GOOD'
        # 'hcal': 'STANDBY'
    }
    
    runs = get_runs(filter=filter_run)
    assert len(runs) > 0

def test_get_runs_with_ignore_filter():
    filter_run = {
        'run_number': {
            'and': [
                {'>': 309000},
                {'<': 310000}
            ]
        }, 
        'oms_attributes.hlt_key': {
            'like': '%commissioning2018%'
        },
        'triplet_summary.dt_triplet.GOOD': {
            '>': 0
        }
    }
    runs = get_runs(filter=filter_run, ignore_filter_transformation=True)
    assert len(runs) > 0

def test_get_runs_not_compressed():
    runs = get_runs(
        filter={
            'run_number': {
                'and': [
                    {'>': 309000},
                    {'<': 310000}
                ]
            },
            'dt': 'GOOD'
        },
        compress_attributes=False
    )
    assert len(runs) > 0

def get_runs_with_combined_filter():
    runs = get_runs(
        filter={
            'run_number': {
                'and': [
                    {'>': 309000},
                    {'<': 310000}
                ]
            # },
            # 'hlt_key': {
            #     'like': '%commissioning2018%'
            # },
            # 'significant': {
            #     '=': True
            }
        }
    )
    print(len(runs))



def test_get_dataset_names_of_run():
    dataset_names = get_dataset_names_of_run(run_number=321777)
    assert len(dataset_names)>0


def test_get_dataset():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    dataset = get_dataset(run_number=run_number, dataset_name=dataset_name)
    print(dataset)
    assert dataset['run_number'] == run_number
    assert dataset['name'] == dataset_name


def test_get_datasets():
    pass


def test_get_lumisections():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_lumisections(run_number, dataset_name)
    print(lumisections)
    assert len(lumisections) > 0


def test_get_oms_lumisections():
    run_number = 328762
    lumisections = get_oms_lumisections(run_number)
    assert len(lumisections) > 0


def test_get_lumisection_ranges():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_lumisection_ranges(run_number, dataset_name)
    assert len(lumisections) > 0


def test_get_oms_lumisection_ranges():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_lumisection_ranges(run_number, dataset_name)
    assert len(lumisections) > 0


def test_get_joint_lumisection_ranges():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_joint_lumisection_ranges(run_number, dataset_name)
    assert len(lumisections) > 0


def test_get_collisions18():
    runs = get_runs(filter={
        'class': 'Collisions18'
    })
    print(runs)


test_get_collisions18()

# TODO
def test_generate_json():
    pass
    # run_number = 328762
    # dataset_name = '/Express/Commissioning2018/DQM'
    # lumisections = get_oms_lumisections(run_number)
    # good_ls_numbers = []
    # for ls_number, lumisection in enumerate(lumisections, start=1):
    #     if lumisection['dt0_ready']:
    #         good_ls_numbers.append(ls_number)
    #     if ls_number<5:
    #         print(lumisection)
    #     # good_ls_numbers.append(ls_number)


