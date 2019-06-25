#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Created by Roberto Preste
import os
import pathlib

# TESTDATA = os.path.join(os.path.dirname(__file__), "test_hmtphenome", "HG00119_filt.vcf")
# print(TESTDATA)
# print(os.path.dirname(__file__))
#
# FIXTURE_DIR = os.path.join(
#     os.path.dirname(os.path.realpath(__file__)),
#     "test_hmtphenome",
#     )
#
# print(FIXTURE_DIR)
#
# p = pathlib.Path(__file__)
# NEW_DIR = p.resolve().parent.joinpath("test_files")
#
# TEST_DIR = os.path.dirname(os.path.realpath(__file__))
# FIXTURE_DIR = os.path.join(TEST_DIR, 'test_hmtnote')
# FIXTURE_FILES = [os.path.join(FIXTURE_DIR, name) for name in ['HG00119_filt.vcf']]
#
# print(TEST_DIR)
# print(FIXTURE_DIR)
# print(FIXTURE_FILES)
# print(NEW_DIR)

# HMTNOTE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
# print(os.path.dirname(os.path.normpath(HMTNOTE_DIR)))
# print(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# print(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
#                    "hmtnote", "hmtnote.py"))
# print(HMTNOTE_DIR)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# print(BASE_DIR)
import requests
import pandas as pd
import asyncio
import aiohttp


def dump_dataframe(dataset: str):
    """
    Download the required dataset from HmtVar's API.
    :param str dataset: name of the dataset to download ('basic',
    'crossref', 'variab', 'predict')
    :return: pd.DataFrame
    """
    url = "https://www.hmtvar.uniba.it/hmtnote/{}".format(dataset)

    # click.echo("Downloading {} dataset... ".format(dataset), nl=False)
    call = requests.get(url)
    resp = call.json()
    # df = pd.DataFrame.from_records(resp)
    # click.echo("Complete!")

    return resp


async def dump_async(dataset: str):
    print("downloading {}".format(dataset))
    url = "https://www.hmtvar.uniba.it/hmtnote/{}".format(dataset)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    return data


async def parse_async(dataframe):
    print("parsing...")
    pass


async def download_data():
    """
    Call the `_dump_dataframe()` function to download the data and store
    them in a single pickled dataframe for later use.
    :return:
    """
    df_basic = await dump_async("basic")
    df_crossref = await dump_async("crossref")
    df_variab = await dump_async("variab")
    df_predict = await dump_async("predict")

    df_crossref.drop(["aa_change", "alt", "disease_score", "locus",
                            "nt_start", "pathogenicity", "ref_rCRS"],
                           axis=1, inplace=True)
    df_variab.drop(["aa_change", "alt", "disease_score", "locus",
                            "nt_start", "pathogenicity", "ref_rCRS"],
                           axis=1, inplace=True)
    df_predict.drop(["aa_change", "alt", "disease_score", "locus",
                            "nt_start", "pathogenicity", "ref_rCRS"],
                           axis=1, inplace=True)
    print("complete")
    # final_df = (df_basic.set_index("id")
    #             .join(df_crossref.set_index("id"))
    #             .join(df_variab.set_index("id"))
    #             .join(df_predict.set_index("id"))).reset_index()
    # final_df.fillna(".", inplace=True)
    #
    # final_df.to_pickle("hmtnote_dump.pkl")

loop = asyncio.get_event_loop()
# loop.run_until_complete(dump_async("basic"))
loop.run_until_complete(download_data())
