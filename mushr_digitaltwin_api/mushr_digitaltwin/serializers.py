from rest_framework import serializers
from django_neomodel import DjangoNode
from mushr_digitaltwin.models import Substrate, Location


class MushRUIDSerializer(serializers.CharField):
    def to_representation(self, instance):
        return (super(MushRUIDSerializer, self).to_representation(instance.uid))

class MushRNodeSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        read_only=True,
        help_text="""Neo4j Internal ID""")
    labels = serializers.ListField(
        child=serializers.CharField(
            help_text="""Neo4j Database Label"""))
    uid = serializers.CharField(
        help_text="""MushR Internal Node UID""",
        read_only=True)


class LocationSerializer(MushRNodeSerializer):
    description = serializers.CharField(
        required=True,
        help_text="""""")
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
    read_only=True)


class MyceliumSampleSerializer(MushRNodeSerializer):
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
    read_only=True)
    weight = serializers.FloatField(required=True,
                                    help_text="""Weight of the Mycelium strain
                                    sample""")

class SpawnSerializer(MyceliumSampleSerializer):
    def to_representation(self, instance):
        instance.is_innoculated_from = instance.is_innoculated_from.all()
        instance.is_contained_by = instance.is_contained_by.all()
        return (super(SpawnSerializer,
                      self).to_representation(instance))

    composition = serializers.CharField(
        required=True,
        help_text="""A description of what
        the spawn is composed of,
        e.g. wheat""")
    volume = serializers.FloatField(
        required=True,
        help_text="""Volume of the Spawn (milliliters)""")
    dateSterilized = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was sterilized""",
    read_only=True)
    createdBy = serializers.CharField(
        help_text="""The user who created
        this node""")
    is_innoculated_from = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of MyceliumSample innoculant"""))
    is_contained_by = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of SpawnContainer that the
            Spawn is/was contained by (if it exists)"""))


class StrainSerializer(MyceliumSampleSerializer):
    source = serializers.CharField(required=False,
                                   help_text="""Some information about where
                                   this strain was sourced/purchased from""")
    species = serializers.CharField(required=True,
                                    help_text="""The Species this strain
                                    belongs to""")
    mushroomCommonName = serializers.CharField(required=False,
                                               help_text="""The name by which
                                               mushrooms of this species are
                                               commonly referred""")

    is_located_at = serializers.ListField(
        help_text="""Location History""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of a Location"""))


class SpawnContainerSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        instance.is_located_at = instance.is_located_at.all()
        instance.currentSpawn = instance.current_spawn()
        instance.currentLocation = instance.current_location()
        return (super(SpawnContainerSerializer,
                      self).to_representation(instance))

    volume = serializers.FloatField(
        required=True,
        help_text="""Volume of the SpawnContainer""")
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
        read_only=True)
    createdBy = serializers.CharField(
        help_text="""The user who created
        this node""")
    is_located_at = serializers.ListField(
        help_text="""Location History""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of a Location"""))

    currentSpawn = serializers.ListField(
        help_text="""Currently occupied Spawn""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of Spawn"""))

    currentLocation = serializers.ListField(
        help_text="""Current location""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""Mushr UID of Location"""))


class SubstrateContainerSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        instance.is_located_at = instance.is_located_at.all()
        instance.currentSubstrate = instance.current_substrate()
        instance.currentLocation = instance.current_location()
        return (super(SubstrateContainerSerializer,
                      self).to_representation(instance))

    description = serializers.CharField(
        required=True,
        help_text="""A description of what
        the substrate is composed of,
        e.g. Straw Pellets""")

    volume = serializers.FloatField(
        required=True,
        help_text="""Volume of the SubstrateContainer""")

    createdBy = serializers.CharField(
        help_text="""The user who created
        this node""")
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
        read_only=True)
    
    is_located_at = serializers.ListField(
        help_text="""Location History""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of a Location"""))

    currentSubstrate = serializers.ListField(
        help_text="""Currently occupied Substrate""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of Substrate"""
        ))

    currentLocation = serializers.ListField(
        help_text="""Current location""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""Mushr UID of Location"""))



class SubstrateSerializer(MushRNodeSerializer):
    
    def to_representation(self, instance):
        instance.is_innoculated_from = instance.is_innoculated_from.all()
        instance.is_contained_by = instance.is_contained_by.all()
        return (super(SubstrateSerializer,
                      self).to_representation(instance))

    weight = serializers.FloatField(
        required=True,
        min_value=0,
        help_text="""Weight of the
          Substrate (g)""")
    volume = serializers.FloatField(
        required=False,
        min_value=0,
        help_text="""Volume of the
          Substrate""")
    composition = serializers.CharField(
        required=True,
        help_text="""A description of what
        the substrate is composed of,
        e.g. Straw Pellets""")
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
          it was created""",
        read_only=True)
    createdBy = serializers.CharField(
        help_text="""The user who
          created this node""",
        required=True)      

    is_innoculated_from = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of MyceliumSample innoculant"""))

    is_contained_by = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of SubstrateContainer that the
            Substrate is/was contained by (if it exists)"""))


class FruitingHoleSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        instance.is_part_of = instance.is_part_of.all()
        return (super(FruitingHoleSerializer,
                      self).to_representation(instance))

    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
        read_only=True)

    is_part_of = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of SubstrateContainer that the
            FruitingHole is a part of (if it exists)"""))


class FlushSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        instance.fruits_from = instance.fruits_from.all()
        instance.fruits_through = instance.fruits_through.all()
        return (super(FlushSerializer,
                      self).to_representation(instance))

    fruits_from = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of Substrate that the
            Flush fruits from"""))

    fruits_through = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of FruitingHole that the
            Flush fruits through"""))

class MushroomHarvestSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        instance.is_harvested_from = instance.is_harvested_from.all()
        return (super(MushroomHarvestSerializer,
                      self).to_representation(instance))
    dateHarvested = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was harvested""",
    read_only=True)

    is_harvested_from = serializers.ListField(
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of Flush that the
            MushroomHarvest is harvested from"""))


class SensorSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        instance.is_harvested_from = instance.is_harvested_from.all()
        return (super(SensorSerializer,
                      self).to_representation(instance))

    url = serializers.CharField(
        required=True,
        help_text="""Unique URL that allows access to
        the sensor data""")

    sensorType = serializers.CharField(
        required=True,
        help_text="""The type/name of the sensor""")

    is_sensing_in = serializers.ListField(
        help_text="""Sensing History""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of GrowChamber that the
            Sensor is sensing in"""))

    dateCreated = serializers.DateTimeField(
        help_text="""The Timestamp at which
        it was created""",
        read_only=True)
