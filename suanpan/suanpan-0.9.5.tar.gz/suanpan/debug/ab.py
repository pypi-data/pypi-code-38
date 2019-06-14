# coding=utf-8
from __future__ import absolute_import, print_function

import requests

from suanpan import asyncio, debug
from suanpan.utils import term

DEFAULT_MARK_PERCENTAGES = (0.5, 0.66, 0.75, 0.8, 0.9, 0.95, 0.98, 0.99, 1)


roundns = lambda s: round(s * 1000, 3)


def printResponseTime(results, markPercentages=DEFAULT_MARK_PERCENTAGES):
    number = len(results)
    costTimes = sorted(
        ({"total": r[0], "response": r[1].elapsed.total_seconds()} for r in results),
        key=lambda t: t["response"],
    )
    responseTimes = [t["response"] for t in costTimes]
    sumTime = sum(responseTimes)
    avgTime = sumTime / number
    minTime = min(responseTimes)
    maxTime = max(responseTimes)

    print()
    term.table(
        [
            ["Response Time:"],
            ["---"],
            ["Sum", "{}ms".format(roundns(sumTime))],
            ["Average", "{}ms".format(roundns(avgTime))],
            ["Min", "{}ms".format(roundns(minTime))],
            ["Max", "{}ms".format(roundns(maxTime))],
        ]
    )

    print()
    print("Percentage of the requests served within a certain time:")
    print("---")
    term.table(
        [
            [
                "{}%".format(int(mp * 100)),
                "{}ms".format(roundns(costTimes[int(number * mp) - 1]["total"])),
                "{}ms".format(roundns(costTimes[int(number * mp) - 1]["response"])),
            ]
            for mp in markPercentages
        ],
        headers=["", "Total", "Response"],
    )

    return results


def test(
    func,
    number,
    concurrency=1,
    thread=True,
    args=None,
    kwargs=None,
    title="ABTest",
    funcName=None,
    markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = args or []
    kwargs = kwargs or {}
    testFunc = lambda x: debug.costCall(func, *args, **kwargs)
    funcName = funcName or func.__name__
    func.__name__ = funcName
    totalTime, results = debug.costCall(
        asyncio.map,
        testFunc,
        range(number),
        workers=concurrency,
        thread=thread,
        pbar=title,
    )
    costTimes = sorted(r[0] for r in results)
    sumTime = sum(costTimes)
    avgTime = sumTime / number
    minTime = min(costTimes)
    maxTime = max(costTimes)

    print()
    print(title)
    print(debug.formatFuncCall(func, *args, **kwargs))
    print("---")
    term.table(
        [
            ["Multi", "Thread" if thread else "Process"],
            ["Number", number],
            ["Concurrency", concurrency],
            [],
            ["Cost Time:"],
            ["Total", "{}ms".format(roundns(totalTime))],
            ["Sum", "{}ms".format(roundns(sumTime))],
            ["Average", "{}ms".format(roundns(avgTime))],
            ["Min", "{}ms".format(roundns(minTime))],
            ["Max", "{}ms".format(roundns(maxTime))],
        ]
    )

    print()
    print("Percentage of the tests served within a certain time:")
    print("---")
    term.table(
        [
            [
                "{}%".format(int(mp * 100)),
                "{}ms".format(roundns(costTimes[int(number * mp) - 1])),
            ]
            for mp in markPercentages
        ]
    )

    return {
        "results": results,
        "cost": {
            "total": totalTime,
            "average": avgTime,
            "min": minTime,
            "max": maxTime,
        },
    }


def request(
    method,
    url,
    number,
    kwargs=None,
    concurrency=1,
    markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = [method, url]
    result = test(
        requests.request,
        number=number,
        concurrency=concurrency,
        args=args,
        kwargs=kwargs,
        title="ABTest - Request - {}".format(method.upper()),
        markPercentages=markPercentages,
    )
    printResponseTime(result["results"], markPercentages=markPercentages)
    return result


def get(
    url,
    number,
    params=None,
    kwargs=None,
    concurrency=1,
    markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = [url]
    kwargs = kwargs or {}
    kwargs.update(params=params)
    result = test(
        requests.get,
        number=number,
        concurrency=concurrency,
        args=args,
        kwargs=kwargs,
        title="ABTest - Request - GET",
        markPercentages=markPercentages,
    )
    printResponseTime(result["results"], markPercentages=markPercentages)
    return result


def post(
    url,
    number,
    data=None,
    json=None,
    kwargs=None,
    concurrency=1,
    markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = [url]
    kwargs = kwargs or {}
    kwargs.update(data=data, json=json)
    result = test(
        requests.post,
        number=number,
        concurrency=concurrency,
        args=args,
        kwargs=kwargs,
        title="ABTest - Request - POST",
        markPercentages=markPercentages,
    )
    printResponseTime(result["results"], markPercentages=markPercentages)
    return result
