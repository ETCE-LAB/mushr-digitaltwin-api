from django.urls import path, register_converter
# from rest_framework.urlpatterns import format_suffix_patterns
from mushr_digitaltwin import views
from mushr_digitaltwin.converters import ISO8601Converter

register_converter(ISO8601Converter, "ISO8601DateTime")

urlpatterns = [

    # Paths for main nodes

    path("substrate/", views.SubstrateUIDs.as_view()),
    path("substrate/<ISO8601DateTime:timestamp>", views.SubstrateUIDs.as_view()),
    path("substrate/<uid>/", views.SubstrateInstance.as_view()),

    path("location/", views.LocationUIDs.as_view()),
    path("location/<ISO8601DateTime:timestamp>", views.LocationUIDs.as_view()),
    path("location/<uid>/", views.LocationInstance.as_view()),

    path("grow_chamber/", views.GrowChamberUIDs.as_view()),
    path("grow_chamber/create", views.CreateGrowChamberInstance.as_view()),
    path("grow_chamber/<ISO8601DateTime:timestamp>", views.GrowChamberUIDs.as_view()),
    path("grow_chamber/<uid>/", views.GrowChamberInstance.as_view()),

    path("storage_location/", views.StorageLocationUIDs.as_view()),
    path("storage_location/create", views.CreateStorageLocationInstance.as_view()),
    path("storage_location/<ISO8601DateTime:timestamp>", views.StorageLocationUIDs.as_view()),
    path("storage_location/<uid>/", views.StorageLocationInstance.as_view()),

    path("mycelium_sample/", views.MyceliumSampleUIDs.as_view()),
    path("mycelium_sample/<ISO8601DateTime:timestamp>", views.MyceliumSampleUIDs.as_view()),
    path("mycelium_sample/<uid>/", views.MyceliumSampleInstance.as_view()),

    path("strain/", views.StrainUIDs.as_view()),
    path("strain/create", views.CreateStrainInstance.as_view()),
    path("strain/<ISO8601DateTime:timestamp>", views.StrainUIDs.as_view()),
    path("strain/<uid>/", views.StrainInstance.as_view()),

    path("spawn/", views.SpawnUIDs.as_view()),
    path("spawn/create/<spawn_container_uid>", views.CreateSpawn.as_view()),
    path("spawn/<ISO8601DateTime:timestamp>", views.SpawnUIDs.as_view()),
    path("spawn/<uid>/", views.SpawnInstance.as_view()),

    path("spawn_container/", views.SpawnContainerUIDs.as_view()),
    path("spawn_container/create", views.CreateSpawnContainerInstance.as_view()),
    path("spawn_container/empty/", views.FreeSpawnContainerUIDs.as_view()),
    path("spawn_container/empty/<ISO8601DateTime:timestamp>", views.FreeSpawnContainerUIDs.as_view()),
    path("spawn_container/<ISO8601DateTime:timestamp>", views.SpawnContainerUIDs.as_view()),
    path("spawn_container/<uid>/", views.SpawnContainerInstance.as_view()),

    path("substrate_container/", views.SubstrateContainerUIDs.as_view()),
    path("substrate_container/create/<int:num_fruiting_holes>", views.CreateSubstrateContainerInstance.as_view()),
    path("substrate_container/empty/", views.FreeSubstrateContainerUIDs.as_view()),
    path("substrate_container/empty/<ISO8601DateTime:timestamp>", views.FreeSubstrateContainerUIDs.as_view()),
    path("substrate_container/<ISO8601DateTime:timestamp>", views.SubstrateContainerUIDs.as_view()),
    path("substrate_container/<uid>/", views.SubstrateContainerInstance.as_view()),

    path("substrate/", views.SubstrateUIDs.as_view()),
    path("substrate/create/<substrate_container_uid>", views.CreateSubstrate.as_view()),
    path("substrate/<ISO8601DateTime:timestamp>", views.SubstrateUIDs.as_view()),
    path("substrate/<uid>/", views.SubstrateInstance.as_view()),

    path("fruiting_hole/", views.FruitingHoleUIDs.as_view()),
    path("fruiting_hole/<ISO8601DateTime:timestamp>", views.FruitingHoleUIDs.as_view()),
    path("fruiting_hole/<uid>/", views.FruitingHoleInstance.as_view()),

    path("flush/", views.FlushUIDs.as_view()),
    path("flush/<ISO8601DateTime:timestamp>", views.FlushUIDs.as_view()),
    path("flush/<uid>/", views.FlushInstance.as_view()),


    path("mushroom_harvest/", views.MushroomHarvestUIDs.as_view()),
    path("mushroom_harvest/<ISO8601DateTime:timestamp>", views.MushroomHarvestUIDs.as_view()),
    path("mushroom_harvest/<uid>/", views.MushroomHarvestInstance.as_view()),

    path("sensor/", views.SensorUIDs.as_view()),
    path("sensor/<ISO8601DateTime:timestamp>", views.SensorUIDs.as_view()),
    path("sensor/<uid>/", views.SensorInstance.as_view()),

    # Paths for specific relationships

    path("relationship/<int:id>", views.MushRRelationshipInstance.as_view()),
]
