import osmnx as ox


class OpenStreet:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        pass

    def get_streets(self, place_name="Barcelona, Spain"):
        # Retrieve the street network for Barcelona
        G = ox.graph_from_place(
            place_name, network_type="drive", simplify=True, retain_all=False
        )
        # Get the list of streets
        streets = [
            data["name"]
            for u, v, key, data in G.edges(keys=True, data=True)
            if "name" in data
        ]
        return streets
