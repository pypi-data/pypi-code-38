class Helper(object):

    @staticmethod
    def print_results(results):
        for result in results:
            print("{}\t{}".format(result.id, result.title))

    @staticmethod
    def print_download_links(resource):
        for season in resource.seasons:
            print("{}".format(season.title))
            for download_link in season.download_links:
                print("{}".format(download_link))
