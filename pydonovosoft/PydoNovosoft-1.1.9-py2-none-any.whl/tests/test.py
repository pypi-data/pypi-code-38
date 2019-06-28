from PydoNovosoft.scope import mprofiler


def main():
    pro = mprofiler.MProfiler("", "", "")
    events = pro.get_messages()["events"]
    for event in events:
        if event["header"]["TemplateId"] == 132 or event["header"]["TemplateId"] == 133:
            print(event)


if __name__ == '__main__':
    main()
