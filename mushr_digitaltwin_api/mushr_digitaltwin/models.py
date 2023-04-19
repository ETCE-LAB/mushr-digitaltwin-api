"""neomodel for neo4j based on MushR OWL ontology

"""

import datetime
from django_neomodel import DjangoNode
from neomodel import (StructuredRel, RelationshipTo)
from neomodel import (RelationshipManager, OUTGOING, INCOMING)
from neomodel import (StringProperty, UniqueIdProperty,
                      DateTimeProperty, FloatProperty)
from neomodel import db

import types


class MushRException(Exception):
    """Exception specific to MushR validation

    """


def custom_rel_merge_helper(lhs, rhs,
                            ident='neomodelident',
                            relation_type=None,
                            direction=None,
                            relation_properties=None,
                            **kwargs):
    """
    Adapted from '_rel_merge_helper'
    Generate a relationship merging string, with specified parameters
    meant for use with CREATE instead of MERGE (Without ON CREATE SET
    ... stuff)

    Examples:
    relation_direction = OUTGOING: (lhs)-[relation_ident:relation_type]->(rhs)
    relation_direction = INCOMING: (lhs)<-[relation_ident:relation_type]-(rhs)
    relation_direction = EITHER: (lhs)-[relation_ident:relation_type]-(rhs)

    :param lhs: The left hand statement.
    :type lhs: str
    :param rhs: The right hand statement.
    :type rhs: str
    :param ident: A specific identity to name the relationship, or None.
    :type ident: str
    :param relation_type: None for all direct rels, * for all of any length, or a name of an explicit rel.
    :type relation_type: str
    :param direction: None or EITHER for all OUTGOING,INCOMING,EITHER. Otherwise OUTGOING or INCOMING.
    :param relation_properties: dictionary of relationship properties to merge
    :returns: string

    """

    if direction == OUTGOING:
        stmt = '-{0}->'
    elif direction == INCOMING:
        stmt = '<-{0}-'
    else:
        stmt = '-{0}-'

    rel_props = ''
    rel_none_props = ''

    if relation_properties:
        rel_props = ' {{{0}}}'.format(', '.join(
            ['{0}: {1}'.format(key, value)
             for key, value in relation_properties.items()
             if value is not None]))

        # if None in relation_properties.values():
        #     rel_none_props = ' ON CREATE SET {0} ON MATCH SET {0}'.format(
        #         ', '.join(
        #             ['{0}.{1}={2}'.format(ident, key, '${!s}'.format(key))
        #              for key, value in relation_properties.items()
        #              if value is None])
        #     )

    # direct, relation_type=None is unspecified, relation_type
    if relation_type is None:
        stmt = stmt.format('')
    # all("*" wildcard) relation_type
    elif relation_type == '*':
        stmt = stmt.format('[*]')
    else:
        # explicit relation_type
        stmt = stmt.format('[{0}:`{1}`{2}]'.format(ident,
                                                   relation_type, rel_props))

    return "({0}){1}({2}){3}".format(lhs, stmt, rhs, rel_none_props)


class CustomRelationshipManager(RelationshipManager):

    def connect_new(self, node, properties=None):
        """
        Connect a node using a new relationship (uses CREATE instead of MERGE)

        :param node:
        :param properties: for the new relationship
        :type: dict
        :return:
        """
        self._check_node(node)

        if not self.definition['model'] and properties:
            raise NotImplementedError(
                "Relationship properties without using a relationship model "
                "is no longer supported."
            )

        params = {}
        rel_model = self.definition['model']
        rp = None  # rel_properties

        if rel_model:
            rp = {}
            # need to generate defaults etc to create fake instance
            tmp = rel_model(**properties) if properties else rel_model()
            # build params and place holders to pass to rel_helper
            for p, v in rel_model.deflate(tmp.__properties__).items():
                if v is not None:
                    rp[p] = '$' + p
                else:
                    rp[p] = None
                params[p] = v

            if hasattr(tmp, 'pre_save'):
                tmp.pre_save()

        new_rel = custom_rel_merge_helper(lhs='us', rhs='them', ident='r',
                                          relation_properties=rp,
                                          **self.definition)
        q = "MATCH (them), (us) WHERE id(them)=$them and id(us)=$self " \
            "CREATE" + new_rel

        params['them'] = node.id

        if not rel_model:
            self.source.cypher(q, params)
            return True

        rel_ = self.source.cypher(q + " RETURN r", params)[0][0][0]
        rel_instance = self._set_start_end_cls(rel_model.inflate(rel_), node)

        if hasattr(rel_instance, 'post_save'):
            rel_instance.post_save()

        return rel_instance


def currenttime():
    """A simple function that returns the current time with timezone

    """
    return datetime.datetime.now().astimezone()


class IsDescendentOf(StructuredRel):
    """Class that contains the abstractions representing the relation
    `IsDescendentOf`

    """


class FruitsFrom(IsDescendentOf):
    """Class that contains the abstractions representing the relation
    `FruitsFrom`

    """


class IsHarvestedFrom(IsDescendentOf):
    """Class that contains the abstractions representing the relation
    `IsDescendentOf`

    """


class IsInnoculatedFrom(IsDescendentOf):
    """Class that contains the abstractions representing the relation
    `IsInnoculatedFrom`

    """
    amount = FloatProperty(required=True,
                           help_text="""The amount of innoculant
                           innoculated (in grams)""")
    timestamp = DateTimeProperty(default=currenttime,
                                 format="%Y-%m-%d %H:%M %Z",
                                 help_text="""The time at which the
                                 innoculation took place""")
    innoculatedBy = StringProperty(help_text="""The user who
    innoculated this spawn""")


class IsLocatedAt(StructuredRel):
    """Class that contains the abstractions representing the relation
    `IsLocatedAt`, for all location related information"""

    start = DateTimeProperty(default=currenttime,
                             format="%Y-%m-%d %H:%M %Z",
                             help_text="""The start time of the time
                             period during which the MushR Asset is
                             located at the Location""")
    end = DateTimeProperty(format="%Y-%m-%d %H:%M %Z",
                           help_text="""The end time of the time
                             period during which the MushR Asset is
                             located at the Location""")
    startBy = StringProperty(required=False,
                             help_text="""The user who set the start
                             of this location period""")
    endBy = StringProperty(required=False,
                           help_text="""The user who set the end
                           of this location period""")


class FruitsThrough(IsLocatedAt):
    """Class that contains the abstractions representing the relation
    `FruitsThrough`, for connecting Flush to FruitingHole"""


class IsContainedBy(IsLocatedAt):
    """Class that contains the abstractions representing the relation
    `IsContainedBy`, for connecting Substrate/Spawn to
    SubstrateContainer/SpawnContainer respectively

    """


class IsPartOf(IsLocatedAt):
    """Class that contains the abstractions representing the relation
    `IsPartOf`, for connecting FruitingHole to SubstrateContainer"""


class IsSensingIn(IsLocatedAt):
    """Class that contains the abstractions representing the relation
    `IsSensingIn`, for connecting Sensor to GrowChamber"""


class Location(DjangoNode):
    """Class that contains the abstractions for all Location-based
    information

    """
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True,
                          required=True,
                          help_text="The name of the Location")
    description = StringProperty(default="", required=False)
    dateCreated = DateTimeProperty(default=currenttime,
                                   format="%Y-%m-%d %H:%M %Z",
                                   help_text="""The timestamp at which
                                   it was created""")


class GrowChamber(Location):
    """Class that contains all the abstractions for the `GrowChamber`
    MushR asset

    """
    pass


class StorageLocation(Location):
    """
    Class that contains all the abstractions for a StorageLocation
    """
    pass


class MyceliumSample(DjangoNode):
    """Class that contains all the abstractions for the `MyceliumSample` MushR
    asset

    """
    uid = UniqueIdProperty()
    dateCreated = DateTimeProperty(required=False,
                                   default=currenttime,
                                   format="%Y-%m-%d %H:%M %Z",
                                   help_text="""The timestamp at which
                                   it was created""")


class Strain(MyceliumSample):
    """Class that contains all the abstractions for the `Strain` MushR
    asset

    """

    uid = UniqueIdProperty()
    weight = FloatProperty(required=True,
                           help_text="""Weight of the Mycelium strain
                           sample""")
    source = StringProperty(required=False,
                            help_text="""Some information about where
                            this strain was sourced/purchased from""")
    species = StringProperty(required=True,
                             help_text="""The Species this strain
                             belongs to""")
    mushroomCommonName = StringProperty(required=False,
                                        help_text="""The name by which
                                        mushrooms of this species are
                                        commonly referred""")
    is_located_at = RelationshipTo(StorageLocation,
                                   "IS_LOCATED_AT",
                                   model=IsLocatedAt)


class SpawnContainer(DjangoNode):
    """Class that contains all the abstractions for the
    `SpawnContainer` MushR asset

    """
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True,
                          required=False,
                          help_text="""The unique name of the
                          SpawnContainer""")

    volume = FloatProperty(required=True,
                           help_text="""Volume of the SpawnContainer""")
    description = StringProperty(required=False,
                                 help_text="""Some description of the
                                 spawn container (e.g. Glass jar with
                                 hole drilled into lid)""")
    createdBy = StringProperty(help_text="""The user who created
    this node""")
    dateCreated = DateTimeProperty(default=currenttime,
                                   help_text="""The timestamp when it
                                   was created""")
    is_located_at = RelationshipTo(StorageLocation,
                                   "IS_LOCATED_AT",
                                   model=IsLocatedAt)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_located_at.connect_new = types.MethodType(
            CustomRelationshipManager.connect_new, self.is_located_at)

    @property
    def current_spawn(self):
        results, columns = self.cypher("""MATCH
        (spawnContainer:SpawnContainer) WHERE
        id(spawnContainer)=$self MATCH
        (spawn:Spawn)-[rel:IS_CONTAINED_BY]->(spawnContainer)
        WHERE NOT EXISTS(rel.end) RETURN spawn""")

        return [Spawn.inflate(row[0]) for row in results]

    @property
    def current_location(self):
        results, columns = self.cypher("""MATCH
        (spawnContainer:SpawnContainer) WHERE
        id(spawnContainer) = $self MATCH
        (spawnContainer)-[rel:IS_LOCATED_AT]->(l:Location) WHERE
        NOT EXISTS(rel.end) return l, rel""")

        return [(Location.inflate(row[0]), IsLocatedAt.inflate(row[1]))
                for row in results]

    @staticmethod
    def get_empty_spawn_containers(timestamp):
        """Returns a list of SpawnContainers which not
        containing any spawn at `timestamp`.

        """
        # Spawn containers that were not new, but still empty at
        # `timestamp`
        empty_spawn_containers, meta = db.cypher_query(
            """MATCH (subc:SpawnContainer)
            WHERE subc.dateCreated <= $timestamp
            AND (:Spawn)-[:IS_CONTAINED_BY]->(subc)
            WITH subc MATCH (:Spawn)-[R:IS_CONTAINED_BY]->(subc)
            WHERE R.start <= $timestamp
            WITH subc, collect(R) as Rcoll
            WHERE all(r in Rcoll WHERE exists(r.end)) return distinct(subc)""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if empty_spawn_containers:
            # If any containers were fetched, select the first
            # column of the results
            empty_spawn_containers = [
                spawn_container[0]
                for spawn_container in empty_spawn_containers]

        # Spawn containers that were new and empty at `timestamp`
        new_spawn_containers, meta = db.cypher_query(
            """MATCH (subc:SpawnContainer)
            WHERE subc.dateCreated <= $timestamp
            AND NOT (subc)<-[:IS_CONTAINED_BY]-(:Spawn)
            RETURN distinct(subc)""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if new_spawn_containers:
            # If any containers were fetched, select the first
            # column of the results
            new_spawn_containers = [
                spawn_container[0]
                for spawn_container in new_spawn_containers]

        return empty_spawn_containers + new_spawn_containers

    def change_storage_location(self, location_uid, transaction=False):
        """Change storage location of the SpawnContainer

        `location_uid` should be a UID of a `Location` (or any
        sub-type of `Location`) node, referring to the new storage
        location

        """

        new_location = Location.nodes.get_or_none(uid=location_uid)

        if not new_location:
            raise """Location UID does not correspond to any
            StorageLocation"""

        current_location = self.current_location()
        if not current_location:
            if transaction:
                with db.transaction:
                    rel = self.is_located_at.connect(new_location)
                    return rel

            else:
                rel = self.is_located_at.connect(new_location)
                return rel

        elif len(current_location) > 1:
            raise """SpawnContainer is erroneously located at
            multiple Locations"""

        current_location, location_rel = (current_location[0][0],
                                          current_location[0][1])

        if transaction:
            with db.transaction:
                location_rel.end = currenttime()
                location_rel.save()
                rel = self.is_located_at.connect_new(new_location)
        else:
            location_rel.end = currenttime()
            location_rel.save()
            rel = self.is_located_at.connect_new(new_location)

        return rel


class Spawn(MyceliumSample):
    """Class that contains all the abstractions for the `Spawn` MushR
    asset

    """
    composition = StringProperty(default="""Wheat""",
                                 help_text="""A description of what
                                 the spawn is composed of, e.g. wheat""")
    volume = FloatProperty(required=False,
                           help_text="""Volume of the Spawn (milliliters)""")
    weight = FloatProperty(required=True,
                           help_text="""Weight of the Spawn (in grams)""")
    dateSterilized = DateTimeProperty(required=False,
                                      format="%Y-%m-%d %H:%M %Z",
                                      help_text="""The timestamp at
                                            which it was sterilized""")
    createdBy = StringProperty(help_text="""The user who created
    this node""")

    is_innoculated_from = RelationshipTo(MyceliumSample,
                                         "IS_INNOCULATED_FROM",
                                         model=IsInnoculatedFrom)
    is_contained_by = RelationshipTo(SpawnContainer,
                                     "IS_CONTAINED_BY",
                                     model=IsContainedBy)

    @property
    def discarded(self):
        """Returns `True` if the Spawn is not contained by a
        SpawnContainer

        """
        spawn_containers = self.is_contained_by.match(
            end__isnull=False).all()
        return bool(spawn_containers)

    @staticmethod
    def get_active_spawn(timestamp):
        """Returns a list of Spawn that are not discarded at
        `timestamp`.

        """
        active_spawn, meta = db.cypher_query(
            """MATCH (sp:Spawn)-[R:IS_CONTAINED_BY]->(spc)
            WHERE R.start <= $timestamp
            AND NOT exists(R.end) OR R.end >= $timestamp
            return sp""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if active_spawn:
            # If any spawn was fetched, select the first column
            active_spawn = [spawn[0] for spawn in active_spawn]

        return active_spawn

    @staticmethod
    def get_innoculable_spawn(timestamp):
        """Returns a list of Spawn that are not discarded and have not
        been innoculated at `timestamp`

        """
        # Spawn that was not discarded at `timestamp` and never
        # innoculated
        not_innoculated_spawn, meta = db.cypher_query(
            """MATCH (sp:Spawn)-[R:IS_CONTAINED_BY]->(spc)
            WHERE (R.start <= $timestamp
            AND (NOT exists(R.end) OR R.end >= $timestamp))
            AND NOT exists((sp)-[:IS_INNOCULATED_FROM]->())
             return sp""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if not_innoculated_spawn:
            # If any spawn was fetched, select the first column
            not_innoculated_spawn = [
                spawn[0] for spawn in not_innoculated_spawn]

        # Spawn that was not discarded at `timestamp` and innoculated
        # after `timestamp`
        innoculated_later_spawn, meta = db.cypher_query(
            """MATCH ()<-[R2:IS_INNOCULATED_FROM]-(sp:Spawn)-[R:IS_CONTAINED_BY]->(spc)
            WHERE (R.start <= $timestamp
            AND (NOT exists(R.end) OR R.end <= $timestamp))
            AND R2.timestamp > $timestamp
             return sp""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if innoculated_later_spawn:
            # If any spawn was fetched, select the first column
            innoculated_later_spawn = [
                spawn[0] for spawn in innoculated_later_spawn]

        return not_innoculated_spawn + innoculated_later_spawn

    @staticmethod
    def create_new(validated_data, spawn_container_uid):
        spawn = Spawn(**validated_data)
        spawn_container = SpawnContainer.nodes.get(uid=spawn_container_uid)
        current_spawn = spawn_container.current_spawn
        if current_spawn:
            raise MushRException(
                f"SpawnContainer(uid={spawn_container_uid}) is currently occupied with Spawn(uid={current_spawn[0].uid})")

        with db.transaction:
            spawn.save()
            spawn.is_contained_by.connect(spawn_container)

        return spawn

    def discard(self):
        """Sets the `end` property of the is_contained_by relationship
        to currenttime

        """
        try:
            substrate_container = self.is_contained_by.all()[0]
        except IndexError:
            raise(MushRException(
                f"Spawn(uid={self.uid}) does not have a container"))

        is_contained_by_relationship = self.is_contained_by.relationship(
            substrate_container)

        with db.transaction:
            is_contained_by_relationship.end = currenttime()
            is_contained_by_relationship.save()


class SubstrateContainer(DjangoNode):
    """Class that contains all the abstractions for the
    `SubstrateContainer` MushR asset

    """
    uid = UniqueIdProperty()

    name = StringProperty(unique_index=True,
                          help_text="""The unique name of the
                          SubstrateContainer""")
    description = StringProperty(required=False,
                                 help_text="""Some optional
                                 description of the
                                 SubstrateContainer""")
    volume = FloatProperty(required=False,
                           help_text="""Volume of the
                           SubstrateContainer""")
    createdBy = StringProperty(help_text="""The user who created
    this node""")
    dateCreated = DateTimeProperty(default=currenttime,
                                   help_text="""The timestamp when it
                                   was created""")
    is_located_at = RelationshipTo(Location,
                                   "IS_LOCATED_AT",
                                   model=IsLocatedAt)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_located_at.connect_new = types.MethodType(
            CustomRelationshipManager.connect_new, self.is_located_at)

    @staticmethod
    def create_with_fh(validated_data, num_fruiting_holes):
        """Create a SubstrateContainer and its fruiting holes

        """
        substrate_container = SubstrateContainer(**validated_data)
        with db.transaction:
            substrate_container.save()
            for i in range(num_fruiting_holes):
                fruiting_hole = FruitingHole()
                fruiting_hole.save()
                fruiting_hole.is_part_of.connect(substrate_container)
        return substrate_container

    @property
    def fruiting_holes(self):
        results, columns = self.cypher("""MATCH
        (substrateContainer:SubstrateContainer) WHERE
        id(substrateContainer)=$self MATCH
        (fruitingHole:FruitingHole)-[rel:IS_PART_OF]->(substrateContainer)
        WHERE NOT EXISTS(rel.end) RETURN fruitingHole""")
        return [FruitingHole.inflate(row[0]) for row in results]

    @property
    def current_substrate(self):

        results, columns = self.cypher("""MATCH
        (substrateContainer:SubstrateContainer) WHERE
        id(substrateContainer)=$self MATCH
        (substrate:Substrate)-[rel:IS_CONTAINED_BY]->(substrateContainer)
        WHERE NOT EXISTS(rel.end) RETURN substrate""")

        return [Substrate.inflate(row[0]) for row in results]

    @property
    def current_location(self):
        results, columns = self.cypher("""MATCH
        (substrateContainer:SubstrateContainer) WHERE
        id(substrateContainer) = $self WITH substrateContainer MATCH
        (substrateContainer)-[rel:IS_LOCATED_AT]->(l:Location) WHERE
        NOT EXISTS(rel.end) return l, rel""")

        return [(Location.inflate(row[0]), IsLocatedAt.inflate(row[1]))
                for row in results]

    def change_storage_location(self, location_uid, transaction=False):
        """Change storage location of the SubstrateContainer

        `location_uid` should be a UID of a `Location` (or any
        sub-type of `Location`) node, referring to the new storage
        location

        """

        new_location = Location.nodes.get_or_none(uid=location_uid)

        if not new_location:
            raise """Location UID does not correspond to any
            StorageLocation"""

        current_location = self.current_location()
        if not current_location:
            if transaction:
                with db.transaction:
                    rel = self.is_located_at.connect(new_location)
                    return rel

            else:
                rel = self.is_located_at.connect(new_location)
                return rel

        elif len(current_location) > 1:
            raise """SubstrateContainer is erroneously located at
            multiple Locations"""

        current_location, location_rel = (current_location[0][0],
                                          current_location[0][1])

        if transaction:
            with db.transaction:
                location_rel.end = currenttime()
                location_rel.save()
                rel = self.is_located_at.connect_new(new_location)
        else:
            location_rel.end = currenttime()
            location_rel.save()
            rel = self.is_located_at.connect_new(new_location)

        return rel

    @staticmethod
    def get_empty_substrate_containers(timestamp):
        """Returns a list of SubstrateContainers which not
        containing any Substrate at `timestamp`.

        """
        # Substrate containers that were not new, but still empty at
        # `timestamp`
        empty_substrate_containers, meta = db.cypher_query(
            """MATCH (subc:SubstrateContainer)
            WHERE subc.dateCreated <= $timestamp
            AND (:Substrate)-[:IS_CONTAINED_BY]->(subc)
            WITH subc MATCH (:Substrate)-[R:IS_CONTAINED_BY]->(subc)
            WHERE R.start <= $timestamp
            WITH subc, collect(R) as Rcoll
            WHERE all(r in Rcoll WHERE exists(r.end)) return distinct(subc)""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if empty_substrate_containers:
            # If any containers were fetched, select the first
            # column of the results
            empty_substrate_containers = [
                substrate_container[0]
                for substrate_container in empty_substrate_containers]

        # Substrate containers that were new and empty at `timestamp`
        new_substrate_containers, meta = db.cypher_query(
            """MATCH (subc:SubstrateContainer)
            WHERE subc.dateCreated <= $timestamp
            AND NOT (subc)<-[:IS_CONTAINED_BY]-(:Substrate)
            RETURN distinct(subc)""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if new_substrate_containers:
            # If any containers were fetched, select the first
            # column of the results
            new_substrate_containers = [
                substrate_container[0]
                for substrate_container in new_substrate_containers]

        return empty_substrate_containers + new_substrate_containers


class Substrate(DjangoNode):
    """Class that contains all the abstractions for the `Substrate`
    MushR asset

    """
    uid = UniqueIdProperty()
    weight = FloatProperty(required=True,
                           help_text="""Weight of the Substrate""")
    volume = FloatProperty(required=False,
                           help_text="""Volume of the Substrate""")
    composition = StringProperty(default="""Straw Pellets""",
                                 help_text="""A description of what
                                 the substrate is composed of,
                                 e.g. Straw Pellets""")
    dateCreated = DateTimeProperty(default=currenttime,
                                   format="%Y-%m-%d %H:%M %Z",
                                   help_text="""The timestamp at which
                                         it was created""")
    dateSterilized = DateTimeProperty(required=False,
                                      format="%Y-%m-%d %H:%M %Z",
                                      help_text="""The timestamp at
                                            which it was sterilized""")
    createdBy = StringProperty(help_text="""The user who created this
    node""",
                               required=False)

    innoculatedBy = StringProperty(help_text="""The user who
    innoculated this substrate""")

    is_innoculated_from = RelationshipTo(MyceliumSample,
                                         "IS_INNOCULATED_FROM",
                                         model=IsInnoculatedFrom)
    is_contained_by = RelationshipTo(SubstrateContainer,
                                     "IS_CONTAINED_BY",
                                     model=IsContainedBy)

    @property
    def discarded(self):
        """Returns `True` if the Substrate is not contained by a
        SubstrateContainer

        """
        substrate_containers = self.is_contained_by.match(
            end__isnull=False).all()
        return bool(substrate_containers)

    @staticmethod
    def get_active_substrate(timestamp):
        """Returns a list of Substrate that are not discarded at
        `timestamp`.

        """
        active_substrate, meta = db.cypher_query(
            """MATCH (sp:Substrate)-[R:IS_CONTAINED_BY]->(spc)
            WHERE R.start <= $timestamp 
            AND NOT exists(R.end) OR R.end >= $timestamp
            return sp""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if active_substrate:
            # If any substrate was fetched, select the first column
            active_substrate = [substrate[0] for substrate in active_substrate]

        return active_substrate

    @staticmethod
    def get_innoculable_substrate(timestamp):
        """Returns a list of Substrate that are not discarded and have not
        been innoculated at `timestamp`

        """
        # Substrate that was not discarded at `timestamp` and never
        # innoculated
        not_innoculated_substrate, meta = db.cypher_query(
            """MATCH (sp:Substrate)-[R:IS_CONTAINED_BY]->(spc)
            WHERE (R.start <= $timestamp
            AND (NOT exists(R.end) OR R.end >= $timestamp))
            AND NOT exists((sp)-[:IS_INNOCULATED_FROM]->())
             return sp""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if not_innoculated_substrate:
            # If any substrate was fetched, select the first column
            not_innoculated_substrate = [
                substrate[0] for substrate in not_innoculated_substrate]

        # Substrate that was not discarded at `timestamp` and innoculated
        # after `timestamp`
        innoculated_later_substrate, meta = db.cypher_query(
            """MATCH ()<-[R2:IS_INNOCULATED_FROM]-(sp:Substrate)-[R:IS_CONTAINED_BY]->(spc)
            WHERE (R.start <= $timestamp
            AND (NOT exists(R.end) OR R.end <= $timestamp))
            AND R2.timestamp > $timestamp
             return sp""",
            {"timestamp": timestamp.timestamp()},
            resolve_objects=True,
            retry_on_session_expire=True)

        if innoculated_later_substrate:
            # If any substrate was fetched, select the first column
            innoculated_later_substrate = [
                substrate[0] for substrate in innoculated_later_substrate]

        return not_innoculated_substrate + innoculated_later_substrate

    @staticmethod
    def create_new(validated_data, substrate_container_uid):
        substrate = Substrate(**validated_data)
        substrate_container = SubstrateContainer.nodes.get(uid=substrate_container_uid)
        current_substrate = substrate_container.current_substrate
        if current_substrate:
            raise MushRException(
                f"SubstrateContainer(uid={substrate_container_uid}) is currently occupied with Substrate(uid={current_substrate[0].uid})")
        with db.transaction:
            substrate.save()
            substrate.is_contained_by.connect(substrate_container)
        return substrate


class FruitingHole(DjangoNode):
    """
    Class that contains the abstractions for the `FruitingHole` MushR asset
    """
    uid = UniqueIdProperty()
    is_part_of = RelationshipTo(SubstrateContainer,
                                "IS_PART_OF",
                                model=IsPartOf)
    dateCreated = DateTimeProperty(default=currenttime,
                                   format="%Y-%m-%d %H:%M %Z",
                                   help_text="""The timestamp at which
                                         it was created""")


class Flush(DjangoNode):
    """
    Class that contains the abstractions for the `Flush` MushR asset
    """
    uid = UniqueIdProperty()

    fruits_from = RelationshipTo(Substrate,
                                 "FRUITS_FROM",
                                 model=FruitsFrom)

    fruits_through = RelationshipTo(FruitingHole,
                                    "FRUITS_THROUGH",
                                    model=FruitsThrough)

    @classmethod
    def fruiting_flushes(self,
                         timestamp=None):
        if timestamp is None:
            timestamp = currenttime()
        flushes, meta = db.cypher_query(f"MATCH (fl:Flush)-[rel:FRUITS_THROUGH]->() WHERE rel.start <= {timestamp.timestamp()} return fl", {}, retry_on_session_expire=True)
        return [Flush.inflate(fl[0]) for fl in flushes]


class MushroomHarvest(DjangoNode):
    """Class that contains all the abstractions for the
    `MushroomHarvest` MushR asset

    """
    uid = UniqueIdProperty()
    weight = FloatProperty(required=True,
                           help_text="""The weight (in grams) of the
                           mushroom harvest""")

    dateHarvested = DateTimeProperty(default=currenttime,
                                     format="%Y-%m-%d %H:%M %Z",
                                     help_text="""The timestamp at
                                           which it was harvested""")
    is_harvested_from = RelationshipTo(Flush,
                                       "IS_HARVESTED_FROM",
                                       model=IsHarvestedFrom)


class Sensor(DjangoNode):
    """
    Class that contains the abstractions for the `Sensor` MushR asset
    """
    uid = UniqueIdProperty()
    url = StringProperty(required=True,
                         help_text="""Unique URL that allows access to
                         the sensor data""")
    sensorType = StringProperty(required=True,
                                help_text="""The type/name of the
                                sensor""")
    is_sensing_in = RelationshipTo(GrowChamber,
                                   "IS_SENSING_IN",
                                   model=IsSensingIn)
    dateCreated = DateTimeProperty(default=currenttime,
                                   format="%Y-%m-%d %H:%M %Z",
                                   help_text="""The timestamp at which
                                   it was created""")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_sensing_in.connect_new = types.MethodType(
            CustomRelationshipManager.connect_new, self.is_sensing_in)
