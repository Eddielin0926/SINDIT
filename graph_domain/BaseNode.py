from dataclasses import dataclass

from dataclasses_json import dataclass_json
from py2neo.ogm import Model, Property

from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)


@dataclass
@dataclass_json
class BaseNode(Model):
    """
    Base node type defining properties every node has
    """

    # Core properties:
    id_short: str = Property()
    iri: str = Property()
    description: str = Property()  # may be None

    # Additional properties for visualization (may initially be empty)
    visualization_positioning_x: float | None = Property(default=None)
    visualization_positioning_y: float | None = Property(default=None)

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """

        if not self.id_short is not None and self.iri is not None:
            raise GraphNotConformantToMetamodelError(self, "Id_short or iri not set.")