from .streamio import get_client, StreamObject

class StreamModelMixin:

    def track_action(self, verb, by = None, create_collection = True, force_update = False):
        """
        # minimal:
        todo.track_action('finish')
        """
        stream = StreamObject(self)
        enriched = None
        if create_collection:
            enriched = stream.enrich(force_update = force_update)

        if by is None:
            by = getattr(self, self.feed_actor_field)

        is_onceoff_action = verb in self.feed_once_off_actions
        activity = stream.perform_action(
            by,
            verb,
            is_onceoff_action=is_onceoff_action
        )
        return {
            "object": enriched,
            "activity": activity
        }