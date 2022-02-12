import json
from math import ceil
import urllib.parse
import urllib.request


class XPort:
    """XPort api client"""

    def __init__(self, host: str) -> None:
        self._host = host

    def covers(self):
        page = 1

        url = "/rollershutter"

        result = self.page_request(url, page)

        entities = []

        remaining_pages = 0

        if result.get("allEntities") > len(result.get("entities")):
            remaining_pages = ceil(
                (result.get("allEntities") - len(result.get("entities")))
                / len(result.get("entities"))
            )

        for entity in result.get("entities"):
            entities.append(entity)

        for _ in range(remaining_pages):
            page = page + 1
            result = self.page_request(url, page)
            for entity in result.get("entities"):
                entities.append(entity)

        return entities

    def outlets_for(self, type: str):
        page = 1

        url = "/outlet"

        result = self.page_request(url, page)

        entities = []

        remaining_pages = 0

        if result.get("allEntities") > len(result.get("entities")):
            remaining_pages = ceil(
                (result.get("allEntities") - len(result.get("entities")))
                / len(result.get("entities"))
            )

        for entity in result.get("entities"):
            if entity.get("homeAssistantType") == type:
                entities.append(entity)

        for _ in range(remaining_pages):
            page = page + 1
            result = self.page_request(url, page)
            for entity in result.get("entities"):
                if entity.get("homeAssistantType") == type:
                    entities.append(entity)

        return entities

    def do_post_request(self, url: str, payload: dict, method: str = "POST"):
        encoded_payload = json.dumps(payload).encode()

        end_point = urllib.parse.urljoin(self._host, url)

        req = urllib.request.Request(end_point, data=encoded_payload, method=method)

        req.add_header("Content-Type", "application/json")

        response = urllib.request.urlopen(req)

        text = response.read()

        return json.loads(text.decode("utf-8"))

    def page_request(self, url: str, page: int = 1):
        payload_data = {"count": 10, "page": page}

        return self.do_post_request(url, payload_data, "PUT")

    def switches(self):
        return self.outlets_for("switch")

    def lights(self):
        return self.outlets_for("light")

    def get_switch(self, name: str):
        return self.do_get_request("outlet", name)

    def get_cover(self, name):
        return self.do_get_request("rollershutter", name)

    def do_get_request(self, type: str, name: str):
        url = "/" + type + "/" + name

        end_point = urllib.parse.urljoin(self._host, url)

        response = urllib.request.urlopen(end_point)

        text = response.read()

        return json.loads(text.decode("utf-8"))

    def do_cover_action(self, name: str, action: str):
        payload_data = {"value": action}

        url = "/rollershutter/do/" + name

        return self.do_post_request(url, payload_data)

    def test(self):
        result: dict = self.page_request("/outlet")

        print(f"Result={result}")

        if result.get("page") >= 1:
            return True

        return False

    def set_state(self, name: str, value: bool):
        payload_data = {"value": value}

        url = "/outlet/updateState/" + name

        return self.do_post_request(url, payload_data)
