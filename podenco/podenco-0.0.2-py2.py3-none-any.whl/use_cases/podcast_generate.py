import os
from shutil import copyfile
import attr

from podenco.serializers import podcast_serializer_rss as ser


@attr.s()
class PodcastGenerate:
    repository = attr.ib()
    output_path: str = attr.ib()

    def execute(self):
        podcast = self.repository.get()

        os.makedirs(self.output_path, exist_ok=True)  # TODO Test exist_ok=True

        with open(self.output_path + "/podcast.rss", "w") as f:
            f.write(ser.PodcastEnconderRSS.serialize(podcast))

        for episode in podcast.episodes:
            os.makedirs(
                self.output_path + "/{}".format(episode.id), exist_ok=True
            )  # TODO Test exist_ok=True
            copyfile(
                episode.audio_file,
                self.output_path + "/{}/audio.mp3".format(episode.id),
            )
