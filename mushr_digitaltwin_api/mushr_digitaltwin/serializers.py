from rest_framework import serializers
from neomodel import db
from mushr_digitaltwin.models import (GrowChamber, StorageLocation,
                                      Strain, SpawnContainer)


class MushRUIDSerializer(serializers.CharField):
    def to_representation(self, instance):
        return (super(MushRUIDSerializer,
                      self).to_representation(instance.uid))


class MushRRelationshipSerializer(serializers.Serializer):
    def to_representation(self, instance):
        instance.__relationship_type__ = str(type(instance).__name__)
        instance.__start_node__ = instance.start_node()
        instance.__start_node_labels__ = reversed(
            instance.start_node().inherited_labels())
        instance.__end_node__ = instance.end_node()
        instance.__end_node_labels__ = reversed(
            instance.end_node().inherited_labels())
        print(instance)
        return (super(MushRRelationshipSerializer,
                      self).to_representation(instance))

    id = serializers.IntegerField(
        read_only=True,
        help_text="""Neo4j Internal ID""")

    __relationship_type__ = serializers.CharField(read_only=True)

    __start_node__ = MushRUIDSerializer(read_only=True)
    __start_node_labels__ = serializers.ListField(
        child=serializers.CharField(),
        read_only=True)
    __end_node__ = MushRUIDSerializer(read_only=True)
    __end_node_labels__ = serializers.ListField(
        child=serializers.CharField(),
        read_only=True)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, validated_data.get(key))
        instance.save()
        return instance


class MushRTraversalSerializer(serializers.ListField):
    def to_representation(self, instance):
        traversal = instance._new_traversal()
        # Get a list of unique connected nodes (Sometimes
        # traversal.all returns duplicate nodes)
        connected_nodes = {node.uid: node for node in traversal.all()}
        instance = [instance.all_relationships(node)
                    for node in connected_nodes.values()]
        instance = [relationship_instance
                    for relationship_instances in instance
                    for relationship_instance in relationship_instances]

        return (super(MushRTraversalSerializer,
                      self).to_representation(instance))


class MushRIsDescendentOfRelationshipSerializer(MushRRelationshipSerializer):
    pass


class MushRIsInnoculatedFromRelationshipSerializer(
        MushRIsDescendentOfRelationshipSerializer):
    amount = serializers.FloatField(required=True,
                                    help_text="""The amount of innoculant
                                    innoculated (in grams)""")
    timestamp = serializers.DateTimeField(required=False,
                                          format="%Y-%m-%d %H:%M %Z",
                                          help_text="""The time at which the
                                          innoculation took place""")
    innoculatedBy = serializers.CharField(
        required=False,
        help_text="""The user who innoculated this spawn""")


class MushRIsLocatedAtRelationshipSerializer(MushRRelationshipSerializer):
    def to_representation(self, instance):
        return (super(MushRIsLocatedAtRelationshipSerializer,
                      self).to_representation(instance))
    start = serializers.DateTimeField(
        help_text="""The start time of the time period during which
        the MushR Asset is located at the Location""",
        read_only=False,
        required=True)

    end = serializers.DateTimeField(
        help_text="""The end time of the time period during which
        the MushR Asset is located at the Location""",
        read_only=False,
        required=False)

    startBy = serializers.CharField(
        required=False,
        read_only=False,
        help_text="""The user who set the start
        of this location period""")

    endBy = serializers.CharField(
        required=False,
        read_only=False,
        help_text="""The user who set the end
        of this location period""")


class MushRNodeSerializer(serializers.Serializer):
    def to_representation(self, instance):
        instance.labels = reversed(instance.inherited_labels())
        return super(MushRNodeSerializer, self).to_representation(instance)

    id = serializers.IntegerField(
        read_only=True,
        help_text="""Neo4j Internal ID""")
    labels = serializers.ListField(
        read_only=True,
        child=serializers.CharField(
            help_text="""Neo4j Database Label"""))
    uid = serializers.CharField(
        help_text="""MushR Internal Node UID""",
        read_only=True)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, validated_data.get(key))
        instance.save()
        return instance


class LocationSerializer(MushRNodeSerializer):
    name = serializers.CharField(
        required=True,
        read_only=False,
        help_text="""Name of the Location""")
    description = serializers.CharField(
        required=False,
        read_only=False,
        help_text="""Description of the Location""")
    dateCreated = serializers.DateTimeField(
        required=False,
        help_text="""The timestamp at which
        it was created""",
        read_only=False)


class GrowChamberSerializer(LocationSerializer):

    @db.transaction
    def create(self, validated_data):
        grow_chamber = GrowChamber(**validated_data)
        grow_chamber.save()
        return grow_chamber


class StorageLocationSerializer(LocationSerializer):

    @db.transaction
    def create(self, validated_data):
        storage_location = StorageLocation(**validated_data)
        storage_location.save()
        return storage_location


class MyceliumSampleSerializer(MushRNodeSerializer):
    dateCreated = serializers.DateTimeField(
        required=False,
        help_text="""The timestamp at which
        it was created""",
        read_only=False)
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
        required=False,
        help_text="""Volume of the Spawn (milliliters)""")
    dateSterilized = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was sterilized""",
        read_only=False,
        required=False)
    createdBy = serializers.CharField(
        required=False,
        help_text="""The user who created
        this node""")
    discarded = serializers.BooleanField(read_only=True,
                                         help_text="""Whether the
                                         Spawn has been discarded""")
    is_innoculated_from = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsInnoculatedFromRelationshipSerializer())
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

    @db.transaction
    def create(self, validated_data):
        strain = Strain(**validated_data)
        strain.save()
        return strain


class SpawnContainerSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        return (super(SpawnContainerSerializer,
                      self).to_representation(instance))

    volume = serializers.FloatField(
        required=True,
        help_text="""Volume of the SpawnContainer""")

    name = serializers.CharField(
        required=False,
        help_text="""A name for the container""")

    description = serializers.CharField(
        required=False,
        help_text="""A description of the container""")

    dateCreated = serializers.DateTimeField(
        required=False,
        help_text="""The timestamp at which
        it was created""",
        read_only=False)
    createdBy = serializers.CharField(
        help_text="""The user who created
        this node""",
        required=False)

    is_located_at = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())

    current_spawn = serializers.ListField(
        help_text="""Currently occupied Spawn""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of Spawn"""))

    current_location = serializers.ListField(
        help_text="""Current location""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""Mushr UID of Location"""))

    @db.transaction
    def create(self, validated_data):
        spawn_container = SpawnContainer(**validated_data)
        spawn_container.save()
        return spawn_container


class SubstrateContainerSerializer(MushRNodeSerializer):
    def to_representation(self, instance):
        return (super(SubstrateContainerSerializer,
                      self).to_representation(instance))

    description = serializers.CharField(
        required=False,
        help_text="""A description of the container""")

    name = serializers.CharField(
        required=False,
        help_text="""A name for the container""")

    volume = serializers.FloatField(
        required=True,
        help_text="""Volume of the SubstrateContainer""")

    createdBy = serializers.CharField(
        required=False,
        help_text="""The user who created
        this node""")

    dateCreated = serializers.DateTimeField(
        required=False,
        help_text="""The timestamp at which
        it was created""",
        read_only=False)

    fruiting_holes = serializers.ListField(
        help_text="""FruitingHoles that are part of the
        SubstrateContainer""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""UID of FruitingHole"""))

    is_located_at = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())

    current_substrate = serializers.ListField(
        help_text="""Currently occupied Substrate""",
        read_only=True,
        child=MushRUIDSerializer(
            help_text="""MushR UID of Substrate"""))

    current_location = serializers.ListField(
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
        read_only=False,
        required=False)
    createdBy = serializers.CharField(
        help_text="""The user who
          created this node""",
        required=False)
    discarded = serializers.BooleanField(read_only=True,
                                         help_text="""Whether the
                                         Substrate has been discarded""")
    is_innoculated_from = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsInnoculatedFromRelationshipSerializer())

    is_contained_by = MushRTraversalSerializer(
        read_only=True,
        child=MushRIsLocatedAtRelationshipSerializer())


class FruitingHoleSerializer(MushRNodeSerializer):
    dateCreated = serializers.DateTimeField(
        help_text="""The timestamp at which
        it was created""",
        read_only=False)

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
        read_only=False)
    weight = serializers.FloatField(
        required=True,
        help_text="""The weight (in grams) of the mushroom harvest""")

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
        read_only=False)
