from abc import ABCMeta, abstractmethod


class PackageBase(metaclass=ABCMeta):
    @property
    @abstractmethod
    def package_name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @property
    @abstractmethod
    def author(self) -> str: ...

    @property
    @abstractmethod
    def copyright(self) -> str: ...

    @property
    @abstractmethod
    def license_name(self) -> str: ...

    @property
    @abstractmethod
    def license_text(self) -> str: ...

    @property
    @abstractmethod
    def repository(self) -> str: ...

    @property
    @abstractmethod
    def notice(self) -> str: ...
