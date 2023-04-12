from rest_framework import serializers
from django_neomodel import DjangoNode
from mushr_digitaltwin.models import Substrate, Location


class MushRUIDSerializer(serializers.CharField):
    def to_representation(self, instance):
        return (super(MushRUIDSerializer, self).to_representation(instance.uid))


class MushRRelationshipSerializer(serializers.Serializer):
    def to_representation(self, instance):
        instance.start_node = instance.start_node()
        instance.end_node = instance.end_node()
        return (super(MushRRelationshipSerializer,
                      self).to_representation(instance))
 
    id = serializers.IntegerField(
        read_only=True,
        help_text="""Neo4j Internal ID""")

    start_node = MushRUIDSerializer()
    end_node = MushRUIDSerializer()

class MushRTraversalSerializer(serializers.ListField):
    def to_representation(self, instance):
        traversal = instance._new_traversal()
        instance = [instance.relationship(node) for node in instance.all()]
        return (super(MushRTraversalSerializer,
                      self).to_representation(instance))


class MushRIsDescendentOfRelationshipSerializer(MushRRelationshipSerializer):
    pass
    

class MushRIsLocatedAtRelationshipSerializer(MushRRelationshipSerializer):
    start = serializers.DateTimeField(
        help_text="""The start time of the time period during which
        the MushR Asset is located at the Location""",
        read_only=True)

    end = serializers.DateTimeField(
        help_text="""The end time of the time period during which
        the MushR Asset is located at the Location""",
        read_only=True)

    startBy = serializers.CharField(
        required=True,
        help_text="""The user who set the start
        of this location period""")

    startBy = serializers.CharField(
        required=True,
        help_text="""The user who set the start
        of this location period""")


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
    is_innoculated_from = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsDescendentOfRelationshipSerializer())
    is_contained_by = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())


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

    is_located_at = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())


class SpawnContainerSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
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
    is_located_at = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())

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
    
    is_located_at = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())

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

    is_innoculated_from = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsDescendentOfRelationshipSerializer())

    is_contained_by = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())


class FruitingHoleSerializer(MushRNodeSerializer):
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
        read_only=True)

    is_part_of = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())


class FlushSerializer(MushRNodeSerializer):
    fruits_from = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsDescendentOfRelationshipSerializer())

    fruits_through = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())

class MushroomHarvestSerializer(MushRNodeSerializer):
    dateHarvested = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was harvested""",
    read_only=True)

    is_harvested_from = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsDescendentOfRelationshipSerializer())
    

class SensorSerializer(MushRNodeSerializer):

    url = serializers.CharField(
        required=True,
        help_text="""Unique URL that allows access to
        the sensor data""")

    sensorType = serializers.CharField(
        required=True,
        help_text="""The type/name of the sensor""")

    is_sensing_in = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())

    dateCreated = serializers.DateTimeField(
        help_text="""The Timestamp at which
        it was created""",
        read_only=True)
