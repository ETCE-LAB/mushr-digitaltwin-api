from mushr_digitaltwin.models import (Location, GrowChamber,
                                      StorageLocation, MyceliumSample,
                                      Strain, Spawn, SpawnContainer,
                                      Substrate, SubstrateContainer,
                                      FruitingHole, Flush,
                                      MushroomHarvest, Sensor)
from mushr_digitaltwin.serializers import (LocationSerializer,
                                           MyceliumSampleSerializer,
                                           StrainSerializer,
                                           SpawnSerializer,
                                           SpawnContainerSerializer,
                                           SubstrateSerializer,
                                           SubstrateContainerSerializer,
                                           FruitingHoleSerializer,
                                           FlushSerializer,
                                           MushroomHarvestSerializer,
                                           SensorSerializer)
import datetime
from django.http import Http404, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class MushRNodeUIDs(APIView):
    """Returns a List of all MushR Node UIDs that were created on or
    before ISO 8601 `timestamp`. If `timestamp` is not specified, then
    current system time is assumed.

    [uid:<string:MushR Internal Node UUID4 hexvalue>]

    """
    @property
    def mushr_model(self):
        return None

    # Since some models do not use "dateCreated" for indicating when
    # the node was created, these need to be handled differently

    def yield_uids(self, timestamp):

        if not timestamp:
            timestamp = datetime.datetime.now()
        try:

            if self.mushr_model == Flush:
                instances = Flush.fruiting_flushes(timestamp=timestamp)
            elif self.mushr_model == MushroomHarvest:
                instances = self.mushr_model.nodes.filter(dateHarvested__lte=timestamp)
            else:
                instances = self.mushr_model.nodes.filter(dateCreated__lte=timestamp)
            for instance in instances:
                yield instance.uid

        except (self.mushr_model.DoesNotExist):
            raise Http404

    def get(self, request, timestamp=None):
        return Response(self.yield_uids(timestamp))


class MushRInstance(APIView):
    """Retrieve instance of a MushR Node

    """
    @property
    def mushr_model(self):
        return None

    # Mapping a model to it's serializer
    serializer_map = {
        Location: LocationSerializer,
        GrowChamber: LocationSerializer,
        StorageLocation: LocationSerializer,
        MyceliumSample: MyceliumSampleSerializer,
        Strain: StrainSerializer,
        Spawn: SpawnSerializer,
        SpawnContainer: SpawnContainerSerializer,
        Substrate: SubstrateSerializer,
        SubstrateContainer: SubstrateContainerSerializer,
        FruitingHole: FruitingHoleSerializer,
        Flush: FlushSerializer,
        MushroomHarvest: MushroomHarvestSerializer,
        Sensor: SensorSerializer}

    def get_node(self, uid):
        try:
            return self.mushr_model.nodes.get(uid=uid)
        except (self.mushr_model.DoesNotExist, AttributeError):
            raise Http404

    def get(self, request, uid, format=None):
        node = self.get_node(uid)
        serializer = MushRInstance.serializer_map[self.mushr_model](node)
        return Response(serializer.data)

    def put(self, request, uid, **kwargs):
        node = self.get_node(uid)
        serializer = MushRInstance.serializer_map[self.mushr_model](node,
                                                                    data=request.data,
                                                                    partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class LocationUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Location

class LocationInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Location

class GrowChamberUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return GrowChamber

class GrowChamberInstance(MushRInstance):
    @property
    def mushr_model(self):
        return GrowChamber

class StorageLocationUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return StorageLocation

class StorageLocationInstance(MushRInstance):
    @property
    def mushr_model(self):
        return StorageLocation

class MyceliumSampleUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return MyceliumSample

class MyceliumSampleInstance(MushRInstance):
    @property
    def mushr_model(self):
        return MyceliumSample

class SpawnUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Spawn

class SpawnInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Spawn

class StrainUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Strain

class StrainInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Strain

class SpawnContainerUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return SpawnContainer

class SpawnContainerInstance(MushRInstance):
    @property
    def mushr_model(self):
        return SpawnContainer

class SubstrateContainerUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return SubstrateContainer

class SubstrateContainerInstance(MushRInstance):
    @property
    def mushr_model(self):
        return SubstrateContainer

class SubstrateUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Substrate

class SubstrateInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Substrate

class FruitingHoleUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return FruitingHole

class FruitingHoleInstance(MushRInstance):
    @property
    def mushr_model(self):
        return FruitingHole

class FlushUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Flush

class FlushInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Flush

class MushroomHarvestUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return MushroomHarvest

class MushroomHarvestInstance(MushRInstance):
    @property
    def mushr_model(self):
        return MushroomHarvest

class SensorUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Sensor

class SensorInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Sensor

