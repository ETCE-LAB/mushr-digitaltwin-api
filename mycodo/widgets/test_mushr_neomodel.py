from mushr_neomodel import (Location, GrowChamber, Flush,
                            FruitingHole, StorageLocation,
                            MushroomHarvest, Spawn, SpawnContainer,
                            Substrate, SubstrateContainer, Strain, Sensor)
from mushr_neomodel import currenttime


class TestFlush:

    def test_creation(self):
        """
        Test Whether Flush nodes are being created
        """

        a = Flush()
        a.save()
        b = Flush.nodes.get_or_none(uid=a.uid)
        assert b

        a.delete()

        b = Flush.nodes.get_or_none(uid=b.uid)
        assert not b

    def testFruiting(self):
        """Test Whether FruitsFrom & FruitsThrough relations are being created

        """
        a = Flush()
        s = Substrate(weight=100)
        h = FruitingHole()
        b = SubstrateContainer(name="B1")

        a.save()
        s.save()
        h.save()
        b.save()

        s.is_contained_by.connect(b)
        h.is_part_of.connect(b)
        a.fruits_through.connect(h)
        a.fruits_from.connect(s)

        assert h in a.fruits_through.all()
        assert s in a.fruits_from.all()

        s.is_contained_by.disconnect(b)
        h.is_part_of.disconnect(b)
        a.fruits_through.disconnect(h)
        a.fruits_from.disconnect(s)

        a.delete()
        s.delete()
        h.delete()
        b.delete()


class TestFruitingHole:

    def test_creation(self):
        """
        Test Whether FruitingHole nodes are being created
        """

        a = FruitingHole()
        a.save()
        b = FruitingHole.nodes.get_or_none(uid=a.uid)
        assert b

        a.delete()

        b = FruitingHole.nodes.get_or_none(uid=b.uid)
        assert not b

    def testIsPartOf(self):
        """Test whether IsContainedBy relations are being created

        """
        a = SubstrateContainer(description="Bucket",
                               name="B1",
                               volume=400)
        b = FruitingHole()
        a.save()
        b.save()

        b.is_part_of.connect(a)

        assert a in b.is_part_of.all()

        b.is_part_of.disconnect(a)
        a.delete()
        b.delete()


class TestLocation:

    def test_creation(self):
        """
        Test Whether Location nodes are being created
        """

        a = Location(name="TestLocation", description="Test Description")
        a.save()
        b = Location.nodes.get_or_none(name="TestLocation")
        assert b

        a.delete()

        b = Location.nodes.get_or_none(name="TestLocation")
        assert not b


class TestGrowChamber:

    def test_creation(self):
        """Test whether GrowChamber nodes are being created
        """
        gc = GrowChamber(name="Tent1", description="This is Tent1")
        gc.save()

        gc2 = GrowChamber.nodes.get_or_none(name="Tent1")
        assert gc2

        gc.delete()

        gc2 = GrowChamber.nodes.get_or_none(name="Tent1")
        assert not gc2

    def test_inheritance(self):
        """Test whether GrowChamber nodes also inherit properties and
        labels from Location

        """
        gc = GrowChamber(name="Tent1", description="This is Tent1")
        gc.save()

        gc2 = Location.nodes.get_or_none(name="Tent1")
        assert gc2

        gc.delete()

        gc2 = Location.nodes.get_or_none(name="Tent1")
        assert not gc2


class TestStorageLocation:

    def test_creation(self):
        """Test whether StorageLocation nodes are being created
        """
        gc = StorageLocation(name="Cupboard1", description="This is Cupboard1")
        gc.save()

        gc2 = StorageLocation.nodes.get_or_none(name="Cupboard1")
        assert gc2

        gc.delete()

        gc2 = StorageLocation.nodes.get_or_none(name="Cupboard1")
        assert not gc2

    def test_inheritance(self):
        """Test whether StorageLocation nodes also inherit properties and
        labels from Location

        """
        gc = StorageLocation(name="Cupboard1", description="This is Cupboard1")
        gc.save()

        gc2 = Location.nodes.get_or_none(name="Cupboard1")
        assert gc2

        gc.delete()

        gc2 = Location.nodes.get_or_none(name="Cupboard1")
        assert not gc2


class TestMushroomHarvest:

    def test_creation(self):
        """Test whether MushroomHarvest nodes are being created
        """
        a = MushroomHarvest(weight=150)
        a.save()

        b = MushroomHarvest.nodes.get_or_none(uid=a.uid,
                                              weight=150.0)
        assert b

        a.delete()

        b = MushroomHarvest.nodes.get_or_none(uid=b.uid)
        assert not b

        def testIsHarvestedFrom(self):
            """Test whether IsHarvestedFrom relations are being
            created

            """
            a = MushroomHarvest(weight=159)
            b = Flush()
            a.save()
            b.save()

            a.is_harvested_from.connect(b)
            assert b in a.is_harvested_from.all()

            a.is_harvested_from.disconnect(b)
            a.delete()
            b.delete()


class TestStrain:

    def test_creation(self):
        """Test whether Strain nodes are being created
        """
        a = Strain(source="Some random dude on the street",
                   species="Pleurotus ostreatus",
                   mushroomCommonName="Oyster Mushroom",
                   weight=19)
        a.save()

        b = Strain.nodes.get_or_none(uid=a.uid)
        assert b

        a.delete()

        b = Strain.nodes.get_or_none(uid=b.uid)
        assert not b


class TestSpawn:

    def test_creation(self):
        """Test whether Spawn nodes are being created
        """
        a = Spawn(composition="Wheat",
                  weight=150,
                  volume=400)
        a.save()

        b = Spawn.nodes.get_or_none(uid=a.uid,
                                    volume=400.0)
        assert b

        a.delete()

        b = Spawn.nodes.get_or_none(uid=b.uid)
        assert not b

    def testInnoculatedFrom(self):
        """Test whether InnoculatedFrom relations are being created

        """
        a = Spawn(composition="Wheat",
                  weight=150,
                  volume=400)
        b = Strain(species="idk",
                   weight=100)
        a.save()
        b.save()
        c = Spawn(composition="Wheat",
                  weight=150,
                  volume=400)
        d = Spawn(weight=100)
        c.save()
        d.save()

        a.is_innoculated_from.connect(b, {"amount": 100})
        c.is_innoculated_from.connect(d, {"amount": 100})
        assert b in a.is_innoculated_from.all()
        assert d in c.is_innoculated_from.all()

        a.is_innoculated_from.disconnect(b)
        c.is_innoculated_from.disconnect(d)
        a.delete()
        b.delete()
        c.delete()
        d.delete()

    def testIsContainedBy(self):
        """Test whether IsContainedBy relations are being created

        """
        a = SpawnContainer(description="Glass Jar",
                           name="J1",
                           volume=400)
        b = Spawn(weight=199)
        a.save()
        b.save()

        b.is_contained_by.connect(a)

        assert a in b.is_contained_by.all()

        b.is_contained_by.disconnect(a)
        a.delete()
        b.delete()


class TestSpawnContainer:

    def test_creation(self):
        """Test whether SpawnContainer nodes are being created
        """
        a = SpawnContainer(description="Glass Jar",
                           name="J1",
                           volume=400)
        a.save()

        b = SpawnContainer.nodes.get_or_none(name="J1")
        assert b

        a.delete()

        b = SpawnContainer.nodes.get_or_none(name="J1")
        assert not b

    def testIsLocatedAt(self):
        """Test whether IsLocatedAt relations are being created
        """
        a = SpawnContainer(description="Glass Jar",
                           name="J1",
                           volume=400)
        b = StorageLocation(name="TestLocation")
        b2 = StorageLocation(name="TestLocation2")
        a.save()
        b.save()
        b2.save()

        rel1 = a.is_located_at.connect(b)

        rel1.end = currenttime()
        rel1.save()
        a.is_located_at.connect(b2)

        assert b in a.is_located_at.all()
        assert b2 in a.is_located_at.all()

        a.is_located_at.disconnect(b)
        a.is_located_at.disconnect(b2)
        a.delete()
        b.delete()
        b2.delete()


class TestSubstrate:

    def test_creation(self):
        """Test whether Spawn nodes are being created
        """
        a = Substrate(composition="Straw Pellets",
                      weight=150,
                      volume=400)
        a.save()

        b = Substrate.nodes.get_or_none(uid=a.uid,
                                        volume=400.0)
        assert b

        a.delete()

        b = Substrate.nodes.get_or_none(uid=b.uid)
        assert not b

    def testInnoculatedFrom(self):
        """Test whether InnoculatedFrom relations are being created

        """
        a = Substrate(composition="Straw Pellets",
                      weight=150,
                      volume=400)
        b = Strain(species="idk",
                   weight=19)
        a.save()
        b.save()
        c = Substrate(composition="Straw Pellets",
                      weight=150,
                      volume=400)
        d = Spawn(weight=100)
        c.save()
        d.save()

        a.is_innoculated_from.connect(b, {"amount": 100})
        c.is_innoculated_from.connect(d, {"amount": 100})
        assert b in a.is_innoculated_from.all()
        assert d in c.is_innoculated_from.all()

        a.is_innoculated_from.disconnect(b)
        c.is_innoculated_from.disconnect(d)
        a.delete()
        b.delete()
        c.delete()
        d.delete()

    def testIsContainedBy(self):
        """Test whether IsContainedBy relations are being created

        """
        a = SpawnContainer(description="Glass Jar",
                           name="J1",
                           volume=400)
        b = Spawn(weight=199)
        a.save()
        b.save()

        b.is_contained_by.connect(a)

        assert a in b.is_contained_by.all()

        b.is_contained_by.disconnect(a)
        a.delete()
        b.delete()


class TestSubstrateContainer:

    def test_creation(self):
        """Test whether SpawnContainer nodes are being created
        """
        a = SubstrateContainer(name="B3",
                               description="PlasticBucket",
                               volume=400)
        a.save()

        b = SubstrateContainer.nodes.get_or_none(name="B3")
        assert b

        a.delete()

        b = SubstrateContainer.nodes.get_or_none(name="B3")
        assert not b

    def testIsLocatedAt(self):
        """Test whether IsLocatedAt relations are being created
        """
        a = SubstrateContainer(description="Bucket",
                               name="B1",
                               volume=400)
        b = StorageLocation(name="TestLocation")
        b2 = StorageLocation(name="TestLocation2")
        a.save()
        b.save()
        b2.save()

        rel1 = a.is_located_at.connect(b)

        rel1.end = currenttime()
        rel1.save()
        a.is_located_at.connect(b2)

        assert b in a.is_located_at.all()
        assert b2 in a.is_located_at.all()

        a.is_located_at.disconnect(b)
        a.is_located_at.disconnect(b2)
        a.delete()
        b.delete()
        b2.delete()


class TestSensor:

    def test_creation(self):
        """Test whether Sensor nodes are being created
        """
        a = Sensor(url="https://mycodo.asdklh.com/asdlkh",
                   sensorType="Temperature")

        a.save()

        b = Sensor.nodes.get_or_none(url="https://mycodo.asdklh.com/asdlkh")
        assert b

        a.delete()

        b = Sensor.nodes.get_or_none(url="https://mycodo.asdklh.com/asdlkh")
        assert not b

    def testIsSensingIn(self):
        """Test whether IsSensingIn relations are being created
        """

        a = Sensor(url="https://mycodo.asdklh.com/asdlkh",
                   sensorType="Temperature")
        g = GrowChamber(name="Tent1")
        a.save()
        g.save()

        a.is_sensing_in.connect(g)

        assert g in a.is_sensing_in.all()

        a.is_sensing_in.disconnect(g)
        a.delete()
        g.delete()
