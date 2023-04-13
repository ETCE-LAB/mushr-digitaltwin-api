from mushr_digitaltwin.models import (Location, GrowChamber,
                                      StorageLocation, MyceliumSample,
                                      Strain, Spawn, SpawnContainer,
                                      Substrate, SubstrateContainer,
                                      FruitingHole, Flush,
                                      MushroomHarvest, Sensor,
                                      IsLocatedAt, FruitsThrough,
                                      IsContainedBy, IsPartOf,
                                      IsSensingIn, IsDescendentOf,
                                      FruitsFrom, IsHarvestedFrom,
                                      IsInnoculatedFrom)
from mushr_digitaltwin.serializers import (LocationSerializer,
                                           GrowChamberSerializer,
                                           StorageLocationSerializer,
                                           MyceliumSampleSerializer,
                                           StrainSerializer,
                                           SpawnSerializer,
                                           SpawnContainerSerializer,
                                           SubstrateSerializer,
                                           SubstrateContainerSerializer,
                                           FruitingHoleSerializer,
                                           FlushSerializer,
                                           MushroomHarvestSerializer,
                                           SensorSerializer,
                                           MushRIsLocatedAtRelationshipSerializer,
                                           MushRIsDescendentOfRelationshipSerializer)
from neomodel import db
import datetime
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response


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
                instances = self.mushr_model.nodes.filter(
                    dateHarvested__lte=timestamp)
            else:
                instances = self.mushr_model.nodes.filter(
                    dateCreated__lte=timestamp)
            for instance in instances:
                yield instance.uid

        except (self.mushr_model.DoesNotExist):
            raise Http404

    def get(self, request, timestamp=None):
        return Response(self.yield_uids(timestamp))


class MushRRelationshipInstance(APIView):
    """Retrieve/update instance of a MushR Relationship"""

    # Mapping a model to its serializer
    serializer_map = {
        IsLocatedAt: MushRIsLocatedAtRelationshipSerializer,
        FruitsThrough: MushRIsLocatedAtRelationshipSerializer,
        IsContainedBy: MushRIsLocatedAtRelationshipSerializer,
        IsPartOf: MushRIsLocatedAtRelationshipSerializer,
        IsSensingIn: MushRIsLocatedAtRelationshipSerializer,
        IsDescendentOf: MushRIsDescendentOfRelationshipSerializer,
        FruitsFrom: MushRIsDescendentOfRelationshipSerializer,
        IsHarvestedFrom: MushRIsDescendentOfRelationshipSerializer,
        IsInnoculatedFrom: MushRIsDescendentOfRelationshipSerializer,
    }

    def get_relationship(self, id):
        """Get a relationship with `id`

        """
        try:
            results, meta = db.cypher_query(
                "MATCH ()-[r]->() where id(r)=$id return r", {"id": id},
                resolve_objects=True)
            return results[0][0]

        except IndexError:
            raise Http404

    def get(self, request, id, format=None):
        relationship = self.get_relationship(id)
        serializer = MushRRelationshipInstance.serializer_map[
            type(relationship)](relationship)

        return Response(serializer.data)

    def post(self, request, id, **kwargs):
        relationship = self.get_relationship(id)
        serializer = MushRRelationshipInstance.serializer_map[
            type(relationship)](relationship,
                                data=request.data,
                                partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class MushRNodeBaseAPIView(APIView):
    @property
    def mushr_model(self):
        return None

    # Mapping a model to its serializer
    serializer_map = {
        Location: LocationSerializer,
        GrowChamber: GrowChamberSerializer,
        StorageLocation: StorageLocationSerializer,
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


class MushRNodeCreationAPIView(MushRNodeBaseAPIView):
    def put(self, request, **kwargs):
        serializer = MushRInstance.serializer_map[self.mushr_model
                                                  ](data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class MushRInstance(MushRNodeBaseAPIView):
    """Retrieve/Update instance of a MushR Node

    """
    def get_node(self, uid):
        try:
            return self.mushr_model.nodes.get(uid=uid)
        except (self.mushr_model.DoesNotExist, AttributeError):
            raise Http404

    def get(self, request, uid, format=None):
        node = self.get_node(uid)
        serializer = MushRInstance.serializer_map[self.mushr_model](node)
        return Response(serializer.data)

    def post(self, request, uid, **kwargs):
        node = self.get_node(uid)
        serializer = MushRInstance.serializer_map[self.mushr_model
                                                  ](node,
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


class CreateGrowChamberInstance(MushRNodeCreationAPIView):
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


class CreateStorageLocationInstance(MushRNodeCreationAPIView):
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


class CreateStrainInstance(MushRNodeCreationAPIView):
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


class CreateSpawnContainerInstance(MushRNodeCreationAPIView):
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


class CreateSubstrateContainerInstance(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return SubstrateContainer

    def put(self, request, num_fruiting_holes, **kwargs):
        """Create a SubstrateContainer and automatically create its
        FruitingHoles.

        `num_fruiting_holes`: a positive integer

        """
        # Create a temporary serializer to validate attributes of the
        # substrate_container
        serializer = SubstrateContainerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            substrate_container = SubstrateContainer.create_with_fh(
                serializer.validated_data, num_fruiting_holes)
            # Initialize the "real" serializer
            serializer = SubstrateContainerSerializer(substrate_container)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


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
