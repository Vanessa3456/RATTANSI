from import_export import resources

from students.models import KraEmployee


class KraEmployeeResource(resources.ModelResource):
    class Meta:
        model=KraEmployee