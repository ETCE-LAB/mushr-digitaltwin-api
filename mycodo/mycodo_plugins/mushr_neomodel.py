"""neomodel for neo4j based on MushR OWL ontology

"""

from neomodel import config as neo4jconfig
import configparser
import datetime
from neomodel import (StructuredNode, StructuredRel, RelationshipTo)
from neomodel import (RelationshipManager, OUTGOING, INCOMING)
from neomodel import (StringProperty, UniqueIdProperty,
                      DateTimeProperty, FloatProperty)
from neomodel import db
import types


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
            ['{0}: {1}'.format(key, value) for key, value in relation_properties.items() if value is not None]))
        # if None in relation_properties.values():
        #     rel_none_props = ' ON CREATE SET {0} ON MATCH SET {0}'.format(
        #         ', '.join(
        #             ['{0}.{1}={2}'.format(ident, key, '${!s}'.format(key)) for key, value in relation_properties.items() if value is None])
        #     )
    # direct, relation_type=None is unspecified, relation_type
    if relation_type is None:
        stmt = stmt.format('')
    # all("*" wildcard) relation_type
    elif relation_type == '*':
        stmt = stmt.format('[*]')
    else:
        # explicit relation_type
        stmt = stmt.format('[{0}:`{1}`{2}]'.format(ident, relation_type, rel_props))

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
                                          relation_properties=rp, **self.definition)
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


def read_config():
    """Read mushr_neomodel.conf and return configparser object

    """
    # TODO: DEFAULT section in config file
    mushr_neomodel_config = configparser.ConfigParser()
    mushr_neomodel_config.read("mushr-neomodel.conf")
    return mushr_neomodel_config


mushr_neomodel_config = read_config()

neo4jconfig.DATABASE_URL = mushr_neomodel_config.get(
    "neo4j",
    "DATABASE_URL",
    fallback="bolt://neo4j:neo4j@localhost:7687")


def set_dburl(dburl):
    """
    Set Neo4j Database URL for connections,
    e.g.: 'bolt://username:password@localhost:7687'
    """
    neo4jconfig.DATABASE_URL = dburl


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


class Location(StructuredNode):
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


class MyceliumSample(StructuredNode):
    """Class that contains all the abstractions for the `MyceliumSample` MushR
    asset

    """
    uid = UniqueIdProperty()
    dateCreated = DateTimeProperty(default=currenttime,
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


class SpawnContainer(StructuredNode):
    """Class that contains all the abstractions for the
    `SpawnContainer` MushR asset

    """
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True,
                          required=True,
                          help_text="""The unique name of the
                          SpawnContainer""")

    volume = FloatProperty(required=True,
                           help_text="""Volume of the SpawnContainer""")
    description = StringProperty(required=True,
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

    def current_location(self):
        results, columns = self.cypher("""MATCH
        (spawnContainer:SpawnContainer) WHERE
        id(spawnContainer) = $self MATCH
        (spawnContainer)-[rel:IS_LOCATED_AT]->(l:Location) WHERE
        NOT EXISTS(rel.end) return l, rel""")

        return [(Location.inflate(row[0]), IsLocatedAt.inflate(row[1]))
                for row in results]

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
    innoculatedBy = StringProperty(help_text="""The user who
    innoculated this spawn""")

    is_innoculated_from = RelationshipTo(MyceliumSample,
                                         "IS_INNOCULATED_FROM",
                                         model=IsInnoculatedFrom)
    is_contained_by = RelationshipTo(SpawnContainer,
                                     "IS_CONTAINED_BY",
                                     model=IsContainedBy)


class SubstrateContainer(StructuredNode):
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
    # TODO: Add volume
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

    def current_substrate(self):

        results, columns = self.cypher("""MATCH
        (substrateContainer:SubstrateContainer) WHERE
        id(substrateContainer)=$self MATCH
        (substrate:Substrate)-[rel:IS_CONTAINED_BY]->(substrateContainer)
        WHERE NOT EXISTS(rel.end) RETURN substrate""")

        return [Substrate.inflate(row[0]) for row in results]

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


class Substrate(StructuredNode):
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
    node""")

    innoculatedBy = StringProperty(help_text="""The user who
    innoculated this spawn""")

    is_innoculated_from = RelationshipTo(MyceliumSample,
                                         "IS_INNOCULATED_FROM",
                                         model=IsInnoculatedFrom)
    is_contained_by = RelationshipTo(SubstrateContainer,
                                     "IS_CONTAINED_BY",
                                     model=IsContainedBy)


class FruitingHole(StructuredNode):
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


class Flush(StructuredNode):
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


class MushroomHarvest(StructuredNode):
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


class Sensor(StructuredNode):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_sensing_in.connect_new = types.MethodType(
            CustomRelationshipManager.connect_new, self.is_sensing_in)
