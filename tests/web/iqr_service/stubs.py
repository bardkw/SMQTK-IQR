"""
Stub abstract class implementations.
"""
from typing import Hashable, Sequence, Tuple

from numpy import ndarray

from smqtk_indexing import NearestNeighborsIndex
from smqtk_descriptors import DescriptorGenerator, DescriptorSet
from smqtk_relevancy import RankRelevancyWithFeedback
from smqtk_classifier import ClassifyDescriptorSupervised


STUB_MODULE_PATH = __name__


class StubDescriptorSet (DescriptorSet):
    @classmethod
    def is_usable(cls):
        return True

    def add_many_descriptors(self, descriptors):
        pass

    def count(self):
        pass

    def iteritems(self):
        pass

    def clear(self):
        pass

    def remove_descriptor(self, uuid):
        pass

    def remove_many_descriptors(self, uuids):
        pass

    def get_config(self):
        pass

    def get_many_descriptors(self, uuids):
        pass

    def has_descriptor(self, uuid):
        pass

    def iterkeys(self):
        pass

    def get_descriptor(self, uuid):
        pass

    def iterdescriptors(self):
        pass

    def add_descriptor(self, descriptor):
        pass


class StubClassifier (ClassifyDescriptorSupervised):
    """
    Classifier stub for testing IqrService.
    """

    @classmethod
    def is_usable(cls):
        return True

    def get_config(self):
        pass

    def get_labels(self):
        pass

    def _classify_arrays(self, array_iter):
        pass

    def has_model(self):
        # To allow training.
        return False

    def _train(self, class_examples, **extra_params):
        pass


class StubDescrGenerator (DescriptorGenerator):
    """
    DescriptorGenerator stub for testing IqrService.
    """

    @classmethod
    def is_usable(cls):
        return True

    def get_config(self):
        pass

    def valid_content_types(self):
        pass

    def _generate_arrays(self, data_iter):
        for _ in data_iter:
            yield None


class StubNearestNeighborIndex (NearestNeighborsIndex):
    """
    NearestNeighborIndex stub for testing IqrService.
    """

    @classmethod
    def is_usable(cls):
        return True

    def get_config(self):
        pass

    def count(self):
        pass

    def _build_index(self, descriptors):
        pass

    def _update_index(self, descriptors):
        pass

    def _remove_from_index(self, uids):
        pass

    def _nn(self, d, n=1):
        pass


class StubRankRelevancyWithFeedback (RankRelevancyWithFeedback):
    """
    RankRelevancyWithFeedback stub for testing IqrService.
    """

    @classmethod
    def is_usable(cls):
        return True

    def get_config(self):
        pass

    def _rank_with_feedback(self,
                            pos: Sequence[ndarray],
                            neg: Sequence[ndarray],
                            pool: Sequence[ndarray],
                            pool_uids: Sequence[Hashable],
                            ) -> Tuple[Sequence[float], Sequence[Hashable]]:
        pass
