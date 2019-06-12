from abc import ABC, abstractmethod, abstractproperty

class GitSource(ABC):
    @abstractmethod
    def git_url(self, name):
        """Returns a URL corresponding to the location of repository {name}. Must
           be git clonable. Does not perform validation (confirm existence)."""
        pass

    @abstractmethod
    def create(self, name, is_private=True):
        """Creates a new repository called {name} within the given source."""
        pass

    @abstractproperty
    def repos(self):
        """Returns all repositories contained within the provided source."""

    @abstractmethod
    def delete(self, name):
        """Deletes the named repository within the given sourc."""
        pass
