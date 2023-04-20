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
from mushr_digitaltwin.models import MushRException
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
import drf_standardized_errors.openapi_serializers as drf_openapi_serializers
import rest_framework.exceptions as drf_exceptions
from neomodel import db
import datetime
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


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

    def put(self, request, id, **kwargs):
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
    def post(self, request, **kwargs):
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

    def put(self, request, uid, **kwargs):
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


class ActiveSpawnUIDs(SpawnUIDs):
    """Returns a list of Spawn UIDs which are not discarded at
     `timestamp`. If `timestamp` is not specified, then current system
     time is assumed.

    """
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now()

        for spawn in Spawn.get_active_spawn(
                timestamp):
            yield spawn.uid


class InnoculableSpawnUIDs(SpawnUIDs):
    """Returns a list of Spawn UIDs which are not discarded and have
     not been innoculated at `timestamp`. If `timestamp` is not
     specified, then current system time is assumed.

    """
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now()

        for spawn in Spawn.get_innoculable_spawn(
                timestamp):
            yield spawn.uid


class CreateSpawn(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return Spawn

    @swagger_auto_schema(
        request_body=SpawnSerializer,
        responses={
            200: SpawnSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self, request, spawn_container_uid, **kwargs):
        """Create Spawn and automatically put it in an empty
        SpawnContainer.

        `spawn_container_uid`: UID of a free spawn container.

        See /spawn_container/empty

        """
        serializer = SpawnSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                spawn = Spawn.create_new(serializer.validated_data,
                                         spawn_container_uid)
                serializer = SpawnSerializer(spawn)
                return Response(serializer.data)
            except SpawnContainer.DoesNotExist:
                raise drf_exceptions.NotFound(
                    f"SpawnContainer(uid={spawn_container_uid}) does not exist")


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


class FreeSpawnContainerUIDs(SpawnContainerUIDs):
    """Returns a list of SpawnContainer UIDs which are not containing
    any Spawn at `timestamp`. If `timestamp` is not specified, then
    current system time is assumed.

    """
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now()
        for spawn_container in SpawnContainer.get_empty_spawn_containers(
                timestamp):
            yield spawn_container.uid


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


class FreeSubstrateContainerUIDs(SubstrateContainerUIDs):
    """Returns a list of SubstrateContainer UIDs which are not containing
    any Spawn at `timestamp`. If `timestamp` is not specified, then
    current system time is assumed.

    """
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now()
        for substrate_container in SubstrateContainer.get_empty_substrate_containers(
                timestamp):
            yield substrate_container.uid


class CreateSubstrateContainerInstance(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return SubstrateContainer

    def post(self, request, num_fruiting_holes, **kwargs):
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


class ActiveSubstrateUIDs(SubstrateUIDs):
    """Returns a list of Substrate UIDs which are not discarded at
     `timestamp`. If `timestamp` is not specified, then current system
     time is assumed.

    """
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now()

        for substrate in Substrate.get_active_substrate(
                timestamp):
            yield substrate.uid


class InnoculableSubstrateUIDs(SubstrateUIDs):
    """Returns a list of Substrate UIDs which are not discarded and have
     not been innoculated at `timestamp`. If `timestamp` is not
     specified, then current system time is assumed.

    """
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now()

        for substrate in Substrate.get_innoculable_substrate(
                timestamp):
            yield substrate.uid


class CreateSubstrate(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return Substrate

    def post(self, request, substrate_container_uid, **kwargs):
        """Create Substrate and automatically put it in a free
        SubstrateContainer.

        `substrate_container_uid`: UID of a free substrate
        container. See TODO: Add avalialable container list view

        """
        serializer = SubstrateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            try:
                substrate = Substrate.create_new(serializer.validated_data,
                                                 substrate_container_uid)
                serializer = SubstrateSerializer(substrate)
                return Response(serializer.data)
            except SubstrateContainer.DoesNotExist:
                return Response({"substrate_container": [
                    f"SubstrateContainer(uid={substrate_container_uid}) does not exist"
                ]}, status=404)
            except MushRException as E:
                return Response({"mushr_exception": [str(E)]}, status=400)
        else:
            return Response(serializer.errors, status=400)


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
