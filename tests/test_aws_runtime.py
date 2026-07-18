from __future__ import annotations

from pathlib import Path

import pytest

from agent_context_gateway.aws_runtime import (
    DynamoContextSliceCache,
    S3ContextStore,
    validate_context_id,
)
from agent_context_gateway.models import ContextSlice, TaskRequest


class FakeS3:
    def __init__(self) -> None:
        self.objects = {
            "sources/team-a/service/prod/main.tf": b'resource "aws_s3_bucket" "example" {}',
            "sources/team-a/README.md": b"# Team A",
        }

    def list_objects_v2(self, **request):
        prefix = request["Prefix"]
        return {
            "Contents": [{"Key": key} for key in self.objects if key.startswith(prefix)],
            "IsTruncated": False,
        }

    def download_file(self, _bucket: str, key: str, destination: str) -> None:
        Path(destination).write_bytes(self.objects[key])


class FakeTable:
    def __init__(self) -> None:
        self.items = {}

    def get_item(self, *, Key, ConsistentRead):
        assert ConsistentRead is True
        item = self.items.get(Key["cache_key"])
        return {"Item": dict(item)} if item else {}

    def put_item(self, *, Item):
        self.items[Item["cache_key"]] = Item

    def update_item(self, *, Key, UpdateExpression, ExpressionAttributeValues):
        assert "ADD hits" in UpdateExpression
        item = self.items[Key["cache_key"]]
        item["hits"] += ExpressionAttributeValues[":one"]
        item["last_accessed_at"] = ExpressionAttributeValues[":now"]


def test_s3_context_store_materializes_named_context() -> None:
    store = S3ContextStore("test-bucket", client=FakeS3())
    with store.materialize("team-a") as root:
        assert (root / "service/prod/main.tf").is_file()
        assert (root / "README.md").read_text() == "# Team A"
    assert not root.exists()


def test_context_id_rejects_path_traversal() -> None:
    with pytest.raises(ValueError):
        validate_context_id("../secrets")


def test_dynamo_cache_round_trip() -> None:
    table = FakeTable()
    cache = DynamoContextSliceCache("unused", table=table)
    task = TaskRequest(task_type="iac_security", path="prod/main.tf", prompt="review")
    context_slice = ContextSlice(
        id="slice-1",
        scope="prod/main.tf",
        slice_type="file",
        facts=["fact"],
        sensitivity="high",
        refs=["prod/main.tf"],
        version="1",
        token_estimate=1,
    )
    assert cache.get(task) is None
    cache.put(task, [context_slice])
    hit = cache.get(task)
    assert hit is not None
    assert hit.slice_ids == ["slice-1"]
    assert hit.hits == 1
