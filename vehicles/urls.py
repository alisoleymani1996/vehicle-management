from django.urls import path
from .views import (
    RedBlueVehiclesView,
    RegisterUserAndVehicleView,
    OldOwnersVehiclesView,
    HeavyVehiclesOnNarrowRoadsView,
    TollCalculationView,
    NearbySmallVehiclesView,
    ViolationOwnersView,
    import_roads,
    import_toll_stations,
    import_owners,
)

urlpatterns = [
    path('vehicles/red-blue/', RedBlueVehiclesView.as_view(), name='red-blue-vehicles'),
    path('register/', RegisterUserAndVehicleView.as_view(), name='register-user-vehicle'),
    path('vehicles/old-owners/', OldOwnersVehiclesView.as_view(), name='old-owners-vehicles'),
    path('vehicles/heavy-narrow-roads/', HeavyVehiclesOnNarrowRoadsView.as_view(), name='heavy-narrow-roads'),
    path('vehicles/toll/<int:vehicle_id>/<str:start_date>/<str:end_date>/', TollCalculationView.as_view(), name='toll-calculation'),
    path('vehicles/near-toll-station/', NearbySmallVehiclesView.as_view(), name='near-toll-station'),
    path('violations/', ViolationOwnersView.as_view(), name='violations'),
    path('import-roads/', import_roads, name='import_roads'),
    path('import-toll-stations/', import_toll_stations, name='import_toll_stations'),
    path('import-owners/', import_owners, name='import_owners'),
]
