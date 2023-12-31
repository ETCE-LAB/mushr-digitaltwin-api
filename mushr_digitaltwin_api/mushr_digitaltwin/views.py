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

from mushr_digitaltwin.models import innoculate, start_fruiting, harvest
from mushr_digitaltwin.models import MushRException

from mushr_digitaltwin.serializers import (
    LocationSerializer, GrowChamberSerializer, StorageLocationSerializer,
    MyceliumSampleSerializer, StrainSerializer, SpawnSerializer,
    SpawnContainerSerializer, SubstrateSerializer,
    SubstrateContainerSerializer, FruitingHoleSerializer, FlushSerializer,
    MushroomHarvestSerializer, SensorSerializer,
    MushRIsLocatedAtRelationshipSerializer,
    MushRIsDescendentOfRelationshipSerializer,
    MushRIsInnoculatedFromRelationshipSerializer)

import drf_standardized_errors.openapi_serializers as drf_openapi_serializers
import rest_framework.exceptions as drf_exceptions
from neomodel import db
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


class MushRNodes(APIView):

    @property
    def mushr_model(self):
        return None

    # Since some models do not use "dateCreated" for indicating when
    # the node was created, these need to be handled differently

    def yield_nodes(self, timestamp):

        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()
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
                serializer = MushRNodeBaseAPIView.serializer_map[self.mushr_model](instance)
                yield serializer.data

        except (self.mushr_model.DoesNotExist):
            raise drf_exceptions.NotFound()

    @swagger_auto_schema(responses={
        200: "List[] of MushR Nodes"})
    def get(self, request, timestamp=None):
        """Returns a List of all MushR Nodes that were created on or
        before ISO 8601 `timestamp`. If `timestamp` is not specified,
        then current system time is assumed.

        """
        return Response(self.yield_nodes(timestamp))


class MushRNodeUIDs(APIView):

    @property
    def mushr_model(self):
        return None

    # Since some models do not use "dateCreated" for indicating when
    # the node was created, these need to be handled differently

    def yield_uids(self, timestamp):

        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()
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
            raise drf_exceptions.NotFound()

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a List of all MushR Node UIDs that were created on
        or before ISO 8601 `timestamp`. If `timestamp` is not
        specified, then current system time is assumed.

        """
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
        IsInnoculatedFrom: MushRIsInnoculatedFromRelationshipSerializer,
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
            raise drf_exceptions.NotFound(
                f"Relationship with id={id} not found")

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
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class MushRIsDescendentOfRelationshipInstance(MushRRelationshipInstance):

    @swagger_auto_schema(
        responses={
            200: MushRIsDescendentOfRelationshipSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, id, format=None):
        return super().get(request, id, format)

    @swagger_auto_schema(
        responses={
            200: MushRIsDescendentOfRelationshipSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, id, **kwargs):
        return super().put(request, id, **kwargs)


class MushRIsLocatedAtRelationshipInstance(MushRRelationshipInstance):

    @swagger_auto_schema(
        responses={
            200: MushRIsLocatedAtRelationshipSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, id, format=None):
        return super().get(request, id, format)

    @swagger_auto_schema(
        responses={
            200: MushRIsLocatedAtRelationshipSerializer,
            400: drf_openapi_serializers.ValidationErrorSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, id, **kwargs):
        return super().put(request, id, **kwargs)


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
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class MushRInstance(MushRNodeBaseAPIView):
    """Retrieve/Update instance of a MushR Node

    """

    def get_node(self, uid):
        try:
            return self.mushr_model.nodes.get(uid=uid)
        except (self.mushr_model.DoesNotExist, AttributeError):
            raise drf_exceptions.NotFound(
                f"{self.mushr_model}(uid={uid}) does not exist")

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
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class LocationUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Location


class LocationNodes(MushRNodes):
    @property
    def mushr_model(self):
        return Location


class LocationInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Location

    @swagger_auto_schema(
        responses={200: LocationSerializer,
                   404: drf_openapi_serializers.ValidationErrorSerializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=LocationSerializer,
        responses={
            200: LocationSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class GrowChamberUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return GrowChamber


class GrowChamberNodes(MushRNodes):
    @property
    def mushr_model(self):
        return GrowChamber


class GrowChamberInstance(MushRInstance):
    @property
    def mushr_model(self):
        return GrowChamber

    @swagger_auto_schema(
        responses={200: GrowChamberSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=GrowChamberSerializer,
        responses={
            200: GrowChamberSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class CreateGrowChamberInstance(MushRNodeCreationAPIView):
    @property
    def mushr_model(self):
        return GrowChamber

    @swagger_auto_schema(
        request_body=GrowChamberSerializer,
        responses={
            200: GrowChamberSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer})
    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class StorageLocationUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return StorageLocation


class StorageLocationNodes(MushRNodes):
    @property
    def mushr_model(self):
        return StorageLocation


class StorageLocationInstance(MushRInstance):
    @property
    def mushr_model(self):
        return StorageLocation

    @swagger_auto_schema(
        responses={200: StorageLocationSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=StorageLocationSerializer,
        responses={
            200: StorageLocationSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class CreateStorageLocationInstance(MushRNodeCreationAPIView):
    @property
    def mushr_model(self):
        return StorageLocation

    @swagger_auto_schema(
        request_body=StorageLocationSerializer,
        responses={
            200: StorageLocationSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer})
    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class MyceliumSampleUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return MyceliumSample


class MyceliumSampleNodes(MushRNodes):
    @property
    def mushr_model(self):
        return MyceliumSample


class MyceliumSampleInstance(MushRInstance):
    @property
    def mushr_model(self):
        return MyceliumSample

    @swagger_auto_schema(
        responses={200: MyceliumSampleSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=MyceliumSampleSerializer,
        responses={
            200: MyceliumSampleSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class SpawnUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Spawn


class SpawnNodes(MushRNodes):
    @property
    def mushr_model(self):
        return Spawn


class SpawnInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Spawn

    @swagger_auto_schema(
        responses={200: SpawnSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=SpawnSerializer,
        responses={
            200: SpawnSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class ActiveSpawnUIDs(SpawnUIDs):
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        for spawn in Spawn.get_active_spawn(
                timestamp):
            yield spawn.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a list of Spawn UIDs which are not discarded at
        `timestamp`. If `timestamp` is not specified, then current
        system time is assumed.

        """
        return (super().get(request, timestamp))


class InnoculableSpawnUIDs(SpawnUIDs):
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        for spawn in Spawn.get_innoculable_spawn(
                timestamp):
            yield spawn.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a list of Spawn UIDs which are not discarded and
        have not been innoculated at `timestamp`. If `timestamp` is
        not specified, then current system time is assumed.

        """
        return (super().get(request, timestamp))


class InnoculatedSpawnUIDs(SpawnUIDs):
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        for spawn in Spawn.get_innoculated_spawn(
                timestamp):
            yield spawn.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a list of Spawn UIDs which are not discarded and
        have been innoculated at `timestamp`. If `timestamp` is not
        specified, then current system time is assumed.

        """
        return (super().get(request, timestamp))


class StrainActiveSpawns(APIView):
    def yield_uids(self, strain_uid, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        strain = Strain.nodes.get_or_none(uid=strain_uid)
        if not strain:
            raise drf_exceptions.NotFound(f"Strain(uid={strain_uid})\
does not exist")

        for spawn in strain.get_active_spawns(
                timestamp):
            yield spawn.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Spawn Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp=None, **kwargs):
        """Returns a list of active spawn UIDs which are descendents
        of this Strain

        """
        return Response(self.yield_uids(uid,
                                        timestamp=timestamp))


class StrainActiveSubstrates(APIView):
    def yield_uids(self, strain_uid, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        strain = Strain.nodes.get_or_none(uid=strain_uid)
        if not strain:
            raise drf_exceptions.NotFound(f"Strain(uid={strain_uid})\
does not exist")

        for substrate in strain.get_active_substrates(
                timestamp):
            yield substrate.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Substrate Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp=None, **kwargs):
        """Returns a list of active substrate UIDs which are descendents
        of this Strain

        """
        return Response(self.yield_uids(uid,
                                        timestamp=timestamp))


class GrowChamberActiveSubstrateContainers(APIView):
    def yield_uids(self, gc_uid, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        gc = GrowChamber.nodes.get_or_none(uid=gc_uid)
        if not gc:
            raise drf_exceptions.NotFound(f"GrowChamber(uid={gc_uid})\
does not exist")

        for substrate_container in gc.get_active_substrate_containers(
                timestamp):
            yield substrate_container.uid

    @swagger_auto_schema(responses={
        200:
        "List[<uid:string>] representing MushR SubstrateContainer Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp=None, **kwargs):
        """Returns a list of active SubstrateContainer UIDs which are
        located at GrowChamber.

        """
        return Response(self.yield_uids(uid,
                                        timestamp=timestamp))


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
                    f"SpawnContainer(uid={spawn_container_uid})\
does not exist")


class DiscardSpawn(APIView):

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: SpawnSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def delete(self, request, spawn_container_uid, **kwargs):
        """Discard Spawn

        <container_uid>: UID of SpawnContainer containing the Spawn
        being discarded

        """
        spawn_container = SpawnContainer.nodes.get_or_none(
            uid=spawn_container_uid)

        if not spawn_container:
            raise drf_exceptions.NotFound(
                f"SpawnContainer(uid={spawn_container_uid}) does not exist")
        spawn = spawn_container.current_spawn
        if not spawn:
            raise MushRException(f"SpawnContainer(uid={spawn_container_uid} \
does not currently contain any spawn)")

        if len(spawn) > 1:
            raise MushRException(f"SpawnContainer(uid={spawn_container_uid}) \
erroneously contains multiple spawn")

        spawn = spawn[0]
        spawn.discard()
        return Response(SpawnSerializer(spawn).data)


class StrainUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Strain


class StrainNodes(MushRNodes):
    @property
    def mushr_model(self):
        return Strain


class StrainInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Strain

    @swagger_auto_schema(
        responses={200: StrainSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=StrainSerializer,
        responses={
            200: StrainSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)



class CreateStrainInstance(MushRNodeCreationAPIView):
    @property
    def mushr_model(self):
        return Strain

    @swagger_auto_schema(
        request_body=StrainSerializer,
        responses={
            200: StrainSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer})
    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class SpawnContainerUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return SpawnContainer


class SpawnContainerNodes(MushRNodes):
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
            timestamp = datetime.datetime.now().astimezone()
        for spawn_container in SpawnContainer.get_empty_spawn_containers(
                timestamp):
            yield spawn_container.uid


class SpawnContainerInstance(MushRInstance):
    @property
    def mushr_model(self):
        return SpawnContainer

    @swagger_auto_schema(
        responses={200: SpawnContainerSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=SpawnContainerSerializer,
        responses={
            200: SpawnContainerSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class CreateSpawnContainerInstance(MushRNodeCreationAPIView):
    @property
    def mushr_model(self):
        return SpawnContainer

    @swagger_auto_schema(
        request_body=SpawnContainerSerializer,
        responses={
            200: SpawnContainerSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer})
    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class ChangeSpawnContainerStorageLocation(APIView):

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: SpawnContainerSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self, request, uid, location_uid):
        """Change storage location of the SpawnContainer

        `uid` should be a UID of a SpawnContainer

        `location_uid` should be a UID of a `Location` (or any
        sub-type of `Location`) node, referring to the new storage
        location

        """
        try:
            spawn_container = SpawnContainer.nodes.get(uid=uid)
        except SpawnContainer.DoesNotExist:
            raise drf_exceptions.NotFound(f"SpawnContainer(uid={uid}) \
does not exist")

        _ = spawn_container.change_storage_location(
            location_uid,
            transaction=True)
        return Response(SpawnContainerSerializer(spawn_container).data)


class SpawnContainerLocationAtTimestamp(APIView):

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp, **kwargs):
        """Get the location of the SpawnContainer at `timestamp`

        """

        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        spawn_container = SpawnContainer.nodes.get_or_none(uid=uid)
        if not spawn_container:
            raise drf_exceptions.NotFound(f"SpawnContainer(uid={uid} \
does not exist)")

        locations = spawn_container.location_at_timestamp(timestamp)

        return Response([location.uid for location in locations])


class SpawnContainerSpawnAtTimestamp(APIView):

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp, **kwargs):
        """Get the spawn contained in the SpawnContainer at
        `timestamp`

        """

        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        spawn_container = SpawnContainer.nodes.get_or_none(uid=uid)
        if not spawn_container:
            raise drf_exceptions.NotFound(f"SpawnContainer(uid={uid} \
does not exist)")

        spawns = spawn_container.spawn_at_timestamp(timestamp)

        return Response([spawn.uid for spawn in spawns])


class SubstrateContainerUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return SubstrateContainer


class SubstrateContainerNodes(MushRNodes):
    @property
    def mushr_model(self):
        return SubstrateContainer


class SubstrateContainerInstance(MushRInstance):
    @property
    def mushr_model(self):
        return SubstrateContainer

    @swagger_auto_schema(
        responses={200: SubstrateContainerSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=SubstrateContainerSerializer,
        responses={
            200: SubstrateContainerSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class FreeSubstrateContainerUIDs(SubstrateContainerUIDs):
    """Returns a list of SubstrateContainer UIDs which are not containing
    any Spawn at `timestamp`. If `timestamp` is not specified, then
    current system time is assumed.

    """

    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()
        for substrate_container\
            in SubstrateContainer.get_empty_substrate_containers(
                timestamp):
            yield substrate_container.uid


class CreateSubstrateContainerInstance(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return SubstrateContainer

    @swagger_auto_schema(
        request_body=SubstrateContainerSerializer,
        responses={
            200: SubstrateContainerSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self, request, num_fruiting_holes, **kwargs):
        """Create a SubstrateContainer and automatically create its
        FruitingHoles.

        `num_fruiting_holes`: a positive integer

        """
        # Create a temporary serializer to validate attributes of the
        # substrate_container
        serializer = SubstrateContainerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            substrate_container = SubstrateContainer.create_with_fh(
                serializer.validated_data, num_fruiting_holes)
            # Initialize the "real" serializer
            serializer = SubstrateContainerSerializer(substrate_container)
            return Response(serializer.data)


class ChangeSubstrateContainerStorageLocation(APIView):

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: SubstrateContainerSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self, request, uid, location_uid):
        """Change storage location of the SubstrateContainer

        `uid` should be a UID of a SubstrateContainer

        `location_uid` should be a UID of a `Location` (or any
        sub-type of `Location`) node, referring to the new storage
        location

        """
        try:
            substrate_container = SubstrateContainer.nodes.get(uid=uid)
        except SubstrateContainer.DoesNotExist:
            raise drf_exceptions.NotFound(f"SubstrateContainer(uid={uid}) \
does not exist")

        _ = substrate_container.change_storage_location(
            location_uid,
            transaction=True)
        return Response(SubstrateContainerSerializer(substrate_container).data)


class SubstrateContainerLocationAtTimestamp(APIView):

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp, **kwargs):
        """Get the location of the SubstrateContainer at `timestamp`

        """

        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        substrate_container = SubstrateContainer.nodes.get_or_none(uid=uid)
        if not substrate_container:
            raise drf_exceptions.NotFound(f"SubstrateContainer(uid={uid} \
does not exist)")

        locations = substrate_container.location_at_timestamp(timestamp)

        return Response([location.uid for location in locations])


class SubstrateContainerSubstrateAtTimestamp(APIView):

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs",
        404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, timestamp, **kwargs):
        """Get the substrate contained in the SubstrateContainer at
        `timestamp`

        """

        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        substrate_container = SubstrateContainer.nodes.get_or_none(uid=uid)
        if not substrate_container:
            raise drf_exceptions.NotFound(f"SubstrateContainer(uid={uid} \
does not exist)")

        substrates = substrate_container.substrate_at_timestamp(timestamp)

        return Response([substrate.uid for substrate in substrates])


class SubstrateUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Substrate


class SubstrateNodes(MushRNodes):
    @property
    def mushr_model(self):
        return Substrate


class SubstrateInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Substrate

    @swagger_auto_schema(
        responses={200: SubstrateSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=SubstrateSerializer,
        responses={
            200: SubstrateSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class ActiveSubstrateUIDs(SubstrateUIDs):
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        for substrate in Substrate.get_active_substrate(
                timestamp):
            yield substrate.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a list of Substrate UIDs which are not discarded at
        `timestamp`. If `timestamp` is not specified, then current
        system time is assumed.

        """
        return (super().get(request, timestamp))


class InnoculableSubstrateUIDs(SubstrateUIDs):
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        for substrate in Substrate.get_innoculable_substrate(
                timestamp):
            yield substrate.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a list of Substrate UIDs which are not discarded
        and have not been innoculated at `timestamp`. If `timestamp`
        is not specified, then current system time is assumed.

        """
        return (super().get(request, timestamp))


class InnoculatedSubstrateUIDs(SubstrateUIDs):
    def yield_uids(self, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        for substrate in Substrate.get_innoculated_substrate(
                timestamp):
            yield substrate.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, timestamp=None):
        """Returns a list of Substrate UIDs which are not discarded
        and have been innoculated at `timestamp`. If `timestamp` is
        not specified, then current system time is assumed.

        """
        return (super().get(request, timestamp))


class CreateSubstrate(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return Substrate

    @swagger_auto_schema(
        request_body=SubstrateSerializer,
        responses={
            200: SubstrateSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self, request, substrate_container_uid, **kwargs):
        """Create Substrate and automatically put it in a free
        SubstrateContainer.

        `substrate_container_uid`: UID of a free substrate
        container. See substrate_container/empty

        """
        serializer = SubstrateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                substrate = Substrate.create_new(serializer.validated_data,
                                                 substrate_container_uid)
                serializer = SubstrateSerializer(substrate)
                return Response(serializer.data)
            except SubstrateContainer.DoesNotExist:
                raise drf_exceptions.NotFound(
                    f"SubstrateContainer(uid={substrate_container_uid})\
does not exist")


class DiscardSubstrate(APIView):

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: SubstrateSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def delete(self, request, substrate_container_uid, **kwargs):
        """Discard Substrate

        <container_uid>: UID of SubstrateContainer containing the
        Substrate being discarded

        """
        substrate_container = SubstrateContainer.nodes.get_or_none(
            uid=substrate_container_uid)

        if not substrate_container:
            raise drf_exceptions.NotFound(
                f"SubstrateContainer(uid={substrate_container_uid}) \
does not exist")
        substrate = substrate_container.current_substrate
        if not substrate:
            raise MushRException(f"SubstrateContainer(uid={substrate_container_uid} \
does not currently contain any substrate)")

        if len(substrate) > 1:
            raise MushRException(f"SubstrateContainer(uid={substrate_container_uid}) \
erroneously contains multiple substrate")

        substrate = substrate[0]
        substrate.discard()
        return Response(SubstrateSerializer(substrate).data)


class FruitingHoleUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return FruitingHole


class FruitingHoleNodes(MushRNodes):
    @property
    def mushr_model(self):
        return FruitingHole


class FruitingHoleInstance(MushRInstance):
    @property
    def mushr_model(self):
        return FruitingHole

    @swagger_auto_schema(
        responses={200: FruitingHoleSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=FruitingHoleSerializer,
        responses={
            200: FruitingHoleSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class AvailableFruitingHoles(APIView):
    def yield_uids(self):
        for fruiting_hole in FruitingHole.available_for_fruiting():
            yield fruiting_hole.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request):
        """Get list of FruitingHole UIDs currently available for
        fruiting.

        List is compiled based on currently innoculated substrates
        that have not been discarded, and their respective substrate
        containers. FruitingHoles that have flushes fruiting from them
        are excluded from this list.

        """
        return Response(self.yield_uids())


class HarvestableFruitingHoles(APIView):
    def yield_uids(self):
        for fruiting_hole in FruitingHole.available_for_harvesting():
            yield fruiting_hole.uid

    @swagger_auto_schema(responses={
        200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request):
        """Get list of FruitingHole UIDs with flushes fruiting through
        currently available for fruiting.

        List is compiled based on currently fruiting flushes that have
        not been harvested.

        """
        return Response(self.yield_uids())


class FruitingHoleActiveFlushes(APIView):
    def yield_uids(self, fruiting_hole, timestamp):
        if not timestamp:
            timestamp = datetime.datetime.now().astimezone()

        active_flushes = fruiting_hole.active_flushes(timestamp)
        for active_flush in active_flushes:
            yield active_flush.uid

    @swagger_auto_schema(
        request_body=None,
        responses={404: drf_openapi_serializers.ErrorResponse404Serializer,
                   200: "List[<uid:string>] representing MushR Node UIDs"})
    def get(self, request, uid, timestamp):
        """Get a list of Flushes that are fruiting through a
        FruitingHole at `timestamp`

        """
        try:
            fruiting_hole = FruitingHole.nodes.get(uid=uid)
        except FruitingHole.DoesNotExist:
            raise drf_exceptions.NotFound(f"FruitingHole(uid={uid} \
does not exist)")

        return Response(self.yield_uids(fruiting_hole, timestamp))


class FlushUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Flush


class FlushNodes(MushRNodes):
    @property
    def mushr_model(self):
        return Flush


class FlushInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Flush

    @swagger_auto_schema(
        responses={200: FlushSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=FlushSerializer,
        responses={
            200: FlushSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class MushroomHarvestUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return MushroomHarvest


class MushroomHarvestNodes(MushRNodes):
    @property
    def mushr_model(self):
        return MushroomHarvest


class MushroomHarvestInstance(MushRInstance):
    @property
    def mushr_model(self):
        return MushroomHarvest

    @swagger_auto_schema(
        responses={200: MushroomHarvestSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=MushroomHarvestSerializer,
        responses={
            200: MushroomHarvestSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class SensorUIDs(MushRNodeUIDs):
    @property
    def mushr_model(self):
        return Sensor


class SensorNodes(MushRNodes):
    @property
    def mushr_model(self):
        return Sensor


class SensorInstance(MushRInstance):
    @property
    def mushr_model(self):
        return Sensor

    @swagger_auto_schema(
        responses={200: SensorSerializer,
                   404: drf_openapi_serializers.ErrorResponse404Serializer})
    def get(self, request, uid, format=None):
        return super().get(request, uid, format)

    @swagger_auto_schema(
        request_body=SensorSerializer,
        responses={
            200: SensorSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def put(self, request, uid, **kwargs):
        return super().put(request, uid, **kwargs)


class CreateSensor(MushRNodeBaseAPIView):
    @property
    def mushr_model(self):
        return Sensor

    @swagger_auto_schema(
        request_body=SensorSerializer,
        responses={
            200: SensorSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self, request, grow_chamber_uid, **kwargs):
        """Create Sensor and automatically put it in a
        GrowChamber.

        `grow_chamber_uid`: UID of a GrowChamber

        """
        serializer = SensorSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                sensor = Sensor.create_new(serializer.validated_data,
                                           grow_chamber_uid)
                serializer = SensorSerializer(sensor)
                return Response(serializer.data)
            except GrowChamber.DoesNotExist:
                raise drf_exceptions.NotFound(
                    f"GrowChamber(uid={grow_chamber_uid})\
does not exist")


class StopSensing(APIView):

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: SensorSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def delete(self, request, uid, **kwargs):
        """Stop Sensing

        `uid`: UID of Sensor

        """
        try:
            sensor = Sensor.nodes.get(
                uid=uid)
            sensor.stop_sensing()
        except Sensor.DoesNotExist:
            raise drf_exceptions.NotFound(
                f"Sensor(uid={uid}) does not exist")

        return Response(SensorSerializer(sensor).data)


class Innoculate(APIView):

    @swagger_auto_schema(
        request_body=MushRIsInnoculatedFromRelationshipSerializer,
        responses={
            200: MushRIsInnoculatedFromRelationshipSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer})
    def post(self, request, innoculant_uid, recipient_container_uid):
        """Innoculate a recipient (Spawn or Substrate) using (Spawn or
        Strain)

        `innoculant_uid` can be either Strain UID or SpawnContainer
        UID (of a currently innoculated Spawn)

        `recipient_container_uid` can be either SpawnContainer UID or
        SubstrateContainer UID (that currently contains an innoculable
        Spawn or Substrate respectively)

        """

        serializer = MushRIsInnoculatedFromRelationshipSerializer(
            data=request.data)

        if serializer.is_valid(raise_exception=True):
            is_innoculated_from_relation = innoculate(
                innoculant_uid,
                recipient_container_uid,
                serializer.validated_data)
            return Response(MushRIsInnoculatedFromRelationshipSerializer(
                is_innoculated_from_relation).data)


class Harvest(APIView):
    @swagger_auto_schema(
        request_body=MushroomHarvestSerializer,
        responses={
            200: MushroomHarvestSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self,
             request,
             fruiting_hole_uid):
        """Harvest Mushrooms.

        `fruiting_hole_uid`: UID of FruitingHole that has an active
        flush fruiting through

        """
        serializer = MushroomHarvestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                mushroom_harvest = harvest(fruiting_hole_uid,
                                           serializer.validated_data)
                return Response(
                    MushroomHarvestSerializer(mushroom_harvest).data)
            except FruitingHole.DoesNotExist:
                raise(drf_exceptions.NotFound(
                    f"FruitingHole(uid={fruiting_hole_uid}) does not exist"))


class StartFruiting(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: FlushSerializer,
            400: drf_openapi_serializers.ValidationErrorResponseSerializer,
            404: drf_openapi_serializers.ErrorResponse404Serializer})
    def post(self,
             request,
             fruiting_hole_uid,
             grow_chamber_uid,
             **kwargs):
        """Start fruiting.

        `fruiting_hole_uid`: UID of FruitingHole that is currently
        available for fruiting (See fruiting_hole/available_for_fruiting).

        `grow_chamber_uid`: UID of a GrowChamber where the
        SubstrateContainer is being placed to fascilitate fruiting
        from the contained substrate (This will implicitly change the
        storage location of the SubstrateContainer).

        """
        try:
            flush = start_fruiting(fruiting_hole_uid, grow_chamber_uid)
        except FruitingHole.DoesNotExist:
            raise drf_exceptions.NotFound(
                f"FruitingHole(uid={fruiting_hole_uid} does not exist)")
        except GrowChamber.DoesNotExist:
            raise drf_exceptions.NotFound(
                f"GrowChamber(uid={grow_chamber_uid} does not exist)")

        return Response(FlushSerializer(flush).data)
